"""LiteLLM custom provider for DDG Agent-Payable Services.

Routes LiteLLM calls through DDG's OpenAI-compatible x402 gateway and pays
per-call automatically (x402 / USDC on Base). Because LiteLLM sits underneath
LangChain, CrewAI, AutoGen, etc., registering DDG here puts it in those agents'
execution path.

    pip install "ddg-agent-services-mcp[openai]" litellm

    import litellm
    from ddg_litellm import register
    register()                       # adds the "ddg/" provider

    resp = litellm.completion(
        model="ddg/glm-4.5-air",
        messages=[{"role": "user", "content": "hi"}],
    )
    print(resp.choices[0].message.content)

Env:
    DDG_AGENT_ID     stable agent id (optional; defaults to "ddg-litellm")
    DDG_PRIVATE_KEY  funded Base USDC wallet key — required for metered routes;
                     omit to use only free/free-trial routes.
"""
from __future__ import annotations

import os

import litellm
from litellm import CustomLLM
from litellm.types.utils import ModelResponse

from ddg_agent_services_mcp import DDGPaidClient

# OpenAI params DDG's gateway understands; forwarded verbatim.
_PASSTHROUGH = (
    "temperature", "max_tokens", "top_p", "stop", "stream", "n", "seed",
    "presence_penalty", "frequency_penalty", "tools", "tool_choice", "response_format",
)


def _client() -> DDGPaidClient:
    aid = os.environ.get("DDG_AGENT_ID", "ddg-litellm")
    # dummy key still allows free/free-trial routes; metered routes need a funded key.
    key = os.environ.get("DDG_PRIVATE_KEY") or ("0x" + "1" * 64)
    return DDGPaidClient(agent_id=aid, private_key=key)


class DDGLLM(CustomLLM):
    """LiteLLM handler that calls DDG's /v1/chat/completions with x402 auto-pay."""

    def _body(self, model: str, messages: list, optional_params: dict | None) -> dict:
        name = model.split("/", 1)[-1] if "/" in model else model
        body = {"model": name, "messages": messages}
        for k in _PASSTHROUGH:
            if optional_params and optional_params.get(k) is not None:
                body[k] = optional_params[k]
        return body

    def completion(self, model, messages, *args, **kwargs) -> ModelResponse:
        resp = _client().post("/v1/chat/completions", self._body(model, messages, kwargs.get("optional_params")))
        if isinstance(resp, dict) and resp.get("error"):
            raise Exception(f"DDG gateway error: {resp.get('error')}: {resp.get('message')}")
        return ModelResponse(**resp)

    async def acompletion(self, model, messages, *args, **kwargs) -> ModelResponse:
        # DDG's client is sync; fine for typical agent loops.
        return self.completion(model, messages, *args, **kwargs)


ddg_llm = DDGLLM()


def register() -> None:
    """Register the ``ddg/<model>`` provider with LiteLLM (idempotent)."""
    existing = [p for p in (litellm.custom_provider_map or []) if p.get("provider") != "ddg"]
    litellm.custom_provider_map = existing + [{"provider": "ddg", "custom_handler": ddg_llm}]
