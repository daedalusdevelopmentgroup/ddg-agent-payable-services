#!/usr/bin/env python3
"""DDG Agent-Payable Services — LangChain + CrewAI tool wrappers.

This module provides ready-to-use tool integrations for AI agent frameworks
that let agents discover and pay for DDG services automatically.

The x402 payment flow:
1. Agent calls a DDG endpoint with X-Agent-Id header
2. DDG returns 402 Payment Required with facilitator challenge
3. Agent signs payment with its wallet private key
4. Agent retries the request with X-PAYMENT header
5. DDG verifies payment and returns the result

Packages required:
    pip install x402 eth-account requests langchain-core
    # or for CrewAI:
    pip install x402 eth-account requests crewai

Usage — LangChain:
    from ddg_agent_tools import DDGSiteAuditTool
    tool = DDGSiteAuditTool(agent_id="my-agent", private_key="0x...")
    result = tool.invoke({"url": "https://example.com"})

Usage — CrewAI:
    from ddg_agent_tools import DDGBrowserProofTool
    tool = DDGBrowserProofTool(agent_id="my-agent", private_key="0x...")
"""

from __future__ import annotations

import json
import os
from typing import Any

import requests
from eth_account import Account
from x402 import (
    x402ClientSync,
    x402ClientConfig,
    parse_payment_required,
    detect_version,
)
from x402.http.x402_http_client import x402HTTPClientSync


# ═══════════════════════════════════════════════════════════════
# Core x402 payment client
# ═══════════════════════════════════════════════════════════════

class DDGPaidClient:
    """HTTP client that automatically handles x402 payment challenges for DDG services."""

    BASE_URL = "https://agents.daedalusdevelopmentgroup.com"

    def __init__(
        self,
        agent_id: str,
        private_key: str,
        base_url: str | None = None,
    ):
        self.agent_id = agent_id
        self.account = Account.from_key(private_key)
        self.base_url = base_url or self.BASE_URL

        # Initialize x402 client and register the EVM 'exact' scheme so
        # payments are actually SIGNED with the agent's wallet (Base = eip155:8453).
        # Requires x402[evm] (web3); degrades gracefully to free/free-trial only.
        self.x402_client = x402ClientSync()
        try:
            from x402.mechanisms.evm.exact import ExactEvmScheme
            self.x402_client.register("eip155:8453", ExactEvmScheme(signer=self.account))
        except Exception:
            pass
        self.x402_http = x402HTTPClientSync(self.x402_client)

    def post(
        self,
        path: str,
        payload: dict[str, Any],
        timeout: int = 120,
    ) -> dict[str, Any]:
        """POST to a DDG endpoint, handling 402 payment challenges automatically.

        Flow:
        1. Send request with agent identity
        2. If 402, parse payment requirement, sign payment, retry
        3. Return the result
        """
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "X-Agent-Id": self.agent_id,
        }

        # First attempt — will likely get 402
        resp = requests.post(
            url, json=payload, headers=headers, timeout=timeout
        )

        if resp.status_code == 402:
            # Parse the payment challenge
            payment_headers = self._handle_402(resp)
            if payment_headers is None:
                return {
                    "error": "payment_failed",
                    "message": "Could not create payment payload for 402 challenge",
                }

            # Retry with payment
            headers.update(payment_headers)
            resp = requests.post(
                url, json=payload, headers=headers, timeout=timeout
            )

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 202:
            # Order accepted — return order info for polling
            return resp.json()
        else:
            try:
                return resp.json()
            except Exception:
                return {
                    "error": f"http_{resp.status_code}",
                    "message": resp.text[:500],
                }

    def get(self, path: str, timeout: int = 30) -> dict[str, Any]:
        """GET from a DDG endpoint (free routes only)."""
        url = f"{self.base_url}{path}"
        headers = {"X-Agent-Id": self.agent_id}
        resp = requests.get(url, headers=headers, timeout=timeout)
        try:
            return resp.json()
        except Exception:
            return {"error": f"http_{resp.status_code}", "message": resp.text[:500]}

    def _handle_402(self, resp: requests.Response) -> dict[str, str] | None:
        """Parse a 402 response and create signed payment headers."""
        try:
            # resp.headers is a case-insensitive dict; pass .get directly (do NOT
            # dict() it — that breaks the SDK's case-insensitive header lookups).
            payment_required = self.x402_http.get_payment_required_response(
                lambda k: resp.headers.get(k),
                resp.content,
            )

            if payment_required is None:
                return None

            # Create the payment payload (signs with the agent's wallet)
            payment_payload = self.x402_http.create_payment_payload(payment_required)
            if payment_payload is None:
                return None

            # Encode as headers for the retry request
            sig_headers = self.x402_http.encode_payment_signature_header(payment_payload)
            return sig_headers

        except Exception as e:
            # Fallback: manual x402 v1 handling
            return self._manual_402_handler(resp)

    def _manual_402_handler(self, resp: requests.Response) -> dict[str, str] | None:
        """Fallback manual 402 handler for simple x402 v1 challenges."""
        try:
            # Get the x-payment-required-v1 header
            v1_raw = resp.headers.get("x-payment-required-v1")
            if not v1_raw:
                return None

            challenge = json.loads(v1_raw)
            accepts = challenge.get("accepts", [])
            if not accepts:
                return None

            # Take the first payment requirement
            req = accepts[0]
            max_amount = req.get("maxAmountRequired", "0")
            network = req.get("network", "eip155:8453")
            asset = req.get("asset", "")
            resource = req.get("resource", "")
            pay_to = req.get("payTo", "")

            # Sign the payment with the agent's wallet
            # For x402 v1, the payment is a signed EVM transaction
            # This is a simplified flow — production needs the facilitator
            payment_header = json.dumps({
                "x402Version": 1,
                "scheme": "exact",
                "network": network,
                "asset": asset,
                "maxAmountRequired": max_amount,
                "resource": resource,
                "payTo": pay_to,
                "payer": self.account.address,
            })

            return {"X-PAYMENT": payment_header}

        except Exception:
            return None


# ═══════════════════════════════════════════════════════════════
# LangChain Tool Wrappers
# ═══════════════════════════════════════════════════════════════

def create_langchain_tools(
    agent_id: str,
    private_key: str,
    base_url: str | None = None,
) -> list:
    """Create a set of LangChain tools for DDG Agent-Payable Services.

    Requires: pip install langchain-core

    Args:
        agent_id: Stable AI agent identifier
        private_key: EVM private key (hex string starting with 0x)
        base_url: DDG base URL (defaults to production)

    Returns:
        List of LangChain BaseTool instances
    """
    from langchain_core.tools import tool

    client = DDGPaidClient(agent_id=agent_id, private_key=private_key, base_url=base_url)

    @tool
    def ddg_site_audit(url: str) -> dict:
        """Run an automated website audit on the given URL. Costs ~$0.75 USDC on Base.
        Returns a structured audit with SEO, performance, and conversion insights.
        First 3 calls are free per agent per 24h."""
        return client.post("/v1/site-audit", {"url": url})

    @tool
    def ddg_browser_proof(url: str, instruction: str = "Capture homepage proof") -> dict:
        """Capture browser-based proof/QA screenshots of a website. Costs ~$2 USDC on Base.
        Returns screenshots and reproducible steps.
        First 2 calls are free per agent per 24h."""
        return client.post("/v1/browser-proof", {"url": url, "instruction": instruction})

    @tool
    def ddg_lead_pack(location: str, vertical: str = "medspa") -> dict:
        """Get a curated local-business lead pack with evidence URLs. Costs ~$5 USDC on Base.
        Returns business names, addresses, and outreach angles.
        First call is free per agent per 24h."""
        return client.post("/v1/lead-pack", {"location": location, "vertical": vertical})

    @tool
    def ddg_prompt_injection_scan(target_url: str) -> dict:
        """Scan a website/API for prompt injection vulnerabilities. Costs ~$2 USDC on Base.
        Returns risk summary and exploit reproduction steps.
        First 2 calls are free per agent per 24h."""
        return client.post("/v1/prompt-injection-scan", {"target_url": target_url})

    @tool
    def ddg_mcp_security_audit(mcp_url: str) -> dict:
        """Audit an MCP server for security issues. Costs ~$12 USDC on Base.
        Returns tool-risk matrix and dangerous capability findings.
        First call is free per agent per 24h."""
        return client.post("/v1/mcp-tool-security-audit", {"mcp_url": mcp_url})

    @tool
    def ddg_agent_readiness_scorecard(target_url: str) -> dict:
        """Score a domain for AI-agent readiness. Returns discovery endpoints, OpenAPI,
        llms.txt, pricing, and payment conformance checks."""
        return client.post("/v1/agent-readiness-scorecard", {"url": target_url})

    # Free tools (no payment needed)
    @tool
    def ddg_json_repair(text: str) -> dict:
        """Repair malformed JSON. Free — no payment required."""
        return client.post("/v1/json-repair", {"text": text})

    @tool
    def ddg_skill_safety_scan(content: str) -> dict:
        """Static security scan of AI skill/prompt content. Free — no payment required."""
        return client.post("/v1/ai-skill-safety-scan", {"content": content})

    @tool
    def ddg_rate_limit_analyzer(headers_json: str) -> dict:
        """Analyze rate-limit headers and recommend retry strategy. Free."""
        return client.post("/v1/rate-limit-analyzer", {"headers": json.loads(headers_json)})

    return [
        ddg_site_audit,
        ddg_browser_proof,
        ddg_lead_pack,
        ddg_prompt_injection_scan,
        ddg_mcp_security_audit,
        ddg_agent_readiness_scorecard,
        ddg_json_repair,
        ddg_skill_safety_scan,
        ddg_rate_limit_analyzer,
    ]


# ═══════════════════════════════════════════════════════════════
# CrewAI Tool Wrappers
# ═══════════════════════════════════════════════════════════════

def create_crewai_tools(
    agent_id: str,
    private_key: str,
    base_url: str | None = None,
) -> list:
    """Create a set of CrewAI tools for DDG Agent-Payable Services.

    Requires: pip install crewai

    Args:
        agent_id: Stable AI agent identifier
        private_key: EVM private key (hex string starting with 0x)
        base_url: DDG base URL (defaults to production)

    Returns:
        List of CrewAI BaseTool instances
    """
    from crewai.tools import BaseTool

    client = DDGPaidClient(agent_id=agent_id, private_key=private_key, base_url=base_url)

    class DDGSiteAuditTool(BaseTool):
        name: str = "ddg_site_audit"
        description: str = (
            "Run an automated website audit on a URL. Returns SEO, performance, "
            "and conversion insights. Costs ~$0.75 USDC. First 3 calls free per 24h."
        )

        def _run(self, url: str) -> str:
            result = client.post("/v1/site-audit", {"url": url})
            return json.dumps(result, indent=2)

    class DDGBrowserProofTool(BaseTool):
        name: str = "ddg_browser_proof"
        description: str = (
            "Capture browser screenshots and QA proof of a website. "
            "Costs ~$2 USDC. First 2 calls free per 24h."
        )

        def _run(self, url: str, instruction: str = "Capture homepage proof") -> str:
            result = client.post("/v1/browser-proof", {"url": url, "instruction": instruction})
            return json.dumps(result, indent=2)

    class DDGLeadPackTool(BaseTool):
        name: str = "ddg_lead_pack"
        description: str = (
            "Get curated local-business leads with outreach angles. "
            "Costs ~$5 USDC. First call free per 24h."
        )

        def _run(self, location: str, vertical: str = "medspa") -> str:
            result = client.post("/v1/lead-pack", {"location": location, "vertical": vertical})
            return json.dumps(result, indent=2)

    class DDGPromptInjectionScanTool(BaseTool):
        name: str = "ddg_prompt_injection_scan"
        description: str = (
            "Scan a website/API for prompt injection vulnerabilities. "
            "Costs ~$2 USDC. First 2 calls free per 24h."
        )

        def _run(self, target_url: str) -> str:
            result = client.post("/v1/prompt-injection-scan", {"target_url": target_url})
            return json.dumps(result, indent=2)

    class DDGMCPSecurityAuditTool(BaseTool):
        name: str = "ddg_mcp_security_audit"
        description: str = (
            "Audit an MCP server for security issues. Returns tool-risk matrix. "
            "Costs ~$12 USDC. First call free per 24h."
        )

        def _run(self, mcp_url: str) -> str:
            result = client.post("/v1/mcp-tool-security-audit", {"mcp_url": mcp_url})
            return json.dumps(result, indent=2)

    class DDGJsonRepairTool(BaseTool):
        name: str = "ddg_json_repair"
        description: str = "Repair malformed JSON. Free — no payment required."

        def _run(self, text: str) -> str:
            result = client.post("/v1/json-repair", {"text": text})
            return json.dumps(result, indent=2)

    class DDGSkillSafetyScanTool(BaseTool):
        name: str = "ddg_skill_safety_scan"
        description: str = "Static security scan of AI skill/prompt content. Free."

        def _run(self, content: str) -> str:
            result = client.post("/v1/ai-skill-safety-scan", {"content": content})
            return json.dumps(result, indent=2)

    return [
        DDGSiteAuditTool(),
        DDGBrowserProofTool(),
        DDGLeadPackTool(),
        DDGPromptInjectionScanTool(),
        DDGMCPSecurityAuditTool(),
        DDGJsonRepairTool(),
        DDGSkillSafetyScanTool(),
    ]


# ═══════════════════════════════════════════════════════════════
# OpenAI Agents SDK Wrappers
# ═══════════════════════════════════════════════════════════════

def create_openai_agents_tools(
    agent_id: str,
    private_key: str,
    base_url: str | None = None,
) -> list:
    """Create OpenAI Agents SDK tools for DDG services.

    Requires: pip install openai-agents

    Usage:
        from agents import Agent, Runner
        tools = create_openai_agents_tools("my-agent", os.environ["EVM_PRIVATE_KEY"])
        agent = Agent(name="DDG Assistant", tools=tools)
        result = Runner.run_sync(agent, "Audit example.com")
    """
    from agents import function_tool

    client = DDGPaidClient(agent_id=agent_id, private_key=private_key, base_url=base_url)

    @function_tool
    def ddg_site_audit(url: str) -> str:
        """Run an automated website audit on the given URL.
        Returns SEO, performance, and conversion insights.
        Costs ~$0.75 USDC on Base. First 3 calls free per 24h."""
        return json.dumps(client.post("/v1/site-audit", {"url": url}))

    @function_tool
    def ddg_prompt_injection_scan(target_url: str) -> str:
        """Scan a website/API for prompt injection vulnerabilities.
        Costs ~$2 USDC on Base. First 2 calls free per 24h."""
        return json.dumps(client.post("/v1/prompt-injection-scan", {"target_url": target_url}))

    @function_tool
    def ddg_mcp_security_audit(mcp_url: str) -> str:
        """Audit an MCP server for security issues.
        Costs ~$12 USDC on Base. First call free per 24h."""
        return json.dumps(client.post("/v1/mcp-tool-security-audit", {"mcp_url": mcp_url}))

    @function_tool
    def ddg_json_repair(text: str) -> str:
        """Repair malformed JSON. Free — no payment required."""
        return json.dumps(client.post("/v1/json-repair", {"text": text}))

    return [ddg_site_audit, ddg_prompt_injection_scan, ddg_mcp_security_audit, ddg_json_repair]


# ═══════════════════════════════════════════════════════════════
# AutoGen Wrappers
# ═══════════════════════════════════════════════════════════════

def create_autogen_tools(
    agent_id: str,
    private_key: str,
    base_url: str | None = None,
) -> list:
    """Create AutoGen FunctionTool instances for DDG services.

    Requires: pip install autogen-core

    Usage:
        from autogen_core.tools import FunctionTool
        tools = create_autogen_tools("my-agent", os.environ["EVM_PRIVATE_KEY"])
        # Pass to AssistantAgent via tools=[...]
    """
    from autogen_core.tools import FunctionTool

    client = DDGPaidClient(agent_id=agent_id, private_key=private_key, base_url=base_url)

    async def _site_audit(url: str) -> str:
        """Run a DDG website audit. Costs ~$0.75 USDC. First 3 free/24h."""
        return json.dumps(client.post("/v1/site-audit", {"url": url}))

    async def _injection_scan(target_url: str) -> str:
        """Scan for prompt injection vulnerabilities. ~$2 USDC. First 2 free/24h."""
        return json.dumps(client.post("/v1/prompt-injection-scan", {"target_url": target_url}))

    async def _mcp_audit(mcp_url: str) -> str:
        """Audit an MCP server. ~$12 USDC. First free/24h."""
        return json.dumps(client.post("/v1/mcp-tool-security-audit", {"mcp_url": mcp_url}))

    async def _json_repair(text: str) -> str:
        """Repair malformed JSON. Free."""
        return json.dumps(client.post("/v1/json-repair", {"text": text}))

    return [
        FunctionTool(_site_audit, description="DDG website audit (paid via x402)"),
        FunctionTool(_injection_scan, description="Prompt injection scan (paid via x402)"),
        FunctionTool(_mcp_audit, description="MCP security audit (paid via x402)"),
        FunctionTool(_json_repair, description="JSON repair (free)"),
    ]


# ═══════════════════════════════════════════════════════════════
# PydanticAI Wrappers
# ═══════════════════════════════════════════════════════════════

def create_pydantic_ai_tools(
    agent_id: str,
    private_key: str,
    base_url: str | None = None,
) -> list:
    """Create PydanticAI-compatible functions for DDG services.

    Requires: pip install pydantic-ai

    Usage:
        from pydantic_ai import Agent
        ddg_tools = create_pydantic_ai_tools("my-agent", os.environ["EVM_PRIVATE_KEY"])
        agent = Agent('openai:gpt-4o', tools=ddg_tools)
    """
    client = DDGPaidClient(agent_id=agent_id, private_key=private_key, base_url=base_url)

    def ddg_site_audit(url: str) -> str:
        """Run an automated website audit. Costs ~$0.75 USDC on Base."""
        return json.dumps(client.post("/v1/site-audit", {"url": url}))

    def ddg_prompt_injection_scan(target_url: str) -> str:
        """Scan for prompt injection vulnerabilities. ~$2 USDC."""
        return json.dumps(client.post("/v1/prompt-injection-scan", {"target_url": target_url}))

    def ddg_mcp_security_audit(mcp_url: str) -> str:
        """Audit an MCP server for security. ~$12 USDC."""
        return json.dumps(client.post("/v1/mcp-tool-security-audit", {"mcp_url": mcp_url}))

    def ddg_json_repair(text: str) -> str:
        """Repair malformed JSON. Free."""
        return json.dumps(client.post("/v1/json-repair", {"text": text}))

    return [ddg_site_audit, ddg_prompt_injection_scan, ddg_mcp_security_audit, ddg_json_repair]


# ═══════════════════════════════════════════════════════════════
# LlamaIndex Wrappers
# ═══════════════════════════════════════════════════════════════

def create_llamaindex_tools(
    agent_id: str,
    private_key: str,
    base_url: str | None = None,
) -> list:
    """Create LlamaIndex FunctionTool instances for DDG services.

    Requires: pip install llama-index

    Usage:
        from llama_index.core.agent.workflow import ReActAgent
        tools = create_llamaindex_tools("my-agent", os.environ["EVM_PRIVATE_KEY"])
        agent = ReActAgent(llm=llm, tools=tools)
    """
    from llama_index.core.tools import FunctionTool

    client = DDGPaidClient(agent_id=agent_id, private_key=private_key, base_url=base_url)

    def ddg_site_audit(url: str) -> str:
        """DDG website audit. Costs ~$0.75 USDC on Base. First 3 free/24h."""
        return json.dumps(client.post("/v1/site-audit", {"url": url}))

    def ddg_prompt_injection_scan(target_url: str) -> str:
        """Scan for prompt injection. ~$2 USDC. First 2 free/24h."""
        return json.dumps(client.post("/v1/prompt-injection-scan", {"target_url": target_url}))

    def ddg_mcp_security_audit(mcp_url: str) -> str:
        """Audit an MCP server. ~$12 USDC. First free/24h."""
        return json.dumps(client.post("/v1/mcp-tool-security-audit", {"mcp_url": mcp_url}))

    def ddg_json_repair(text: str) -> str:
        """Repair malformed JSON. Free."""
        return json.dumps(client.post("/v1/json-repair", {"text": text}))

    return [
        FunctionTool.from_defaults(ddg_site_audit),
        FunctionTool.from_defaults(ddg_prompt_injection_scan),
        FunctionTool.from_defaults(ddg_mcp_security_audit),
        FunctionTool.from_defaults(ddg_json_repair),
    ]


# ═══════════════════════════════════════════════════════════════
# Google ADK Wrappers
# ═══════════════════════════════════════════════════════════════

def create_google_adk_tools(
    agent_id: str,
    private_key: str,
    base_url: str | None = None,
) -> list:
    """Create Google ADK tool functions for DDG services.

    Requires: pip install google-adk

    Usage:
        from google.adk.agents import LlmAgent
        tools = create_google_adk_tools("my-agent", os.environ["EVM_PRIVATE_KEY"])
        agent = LlmAgent(name="ddg", model="gemini-2.5-flash", tools=tools)
    """
    client = DDGPaidClient(agent_id=agent_id, private_key=private_key, base_url=base_url)

    def ddg_site_audit(url: str) -> str:
        """Run a DDG automated website audit. Costs ~$0.75 USDC on Base."""
        return json.dumps(client.post("/v1/site-audit", {"url": url}))

    def ddg_prompt_injection_scan(target_url: str) -> str:
        """Scan for prompt injection vulnerabilities. ~$2 USDC."""
        return json.dumps(client.post("/v1/prompt-injection-scan", {"target_url": target_url}))

    def ddg_mcp_security_audit(mcp_url: str) -> str:
        """Audit an MCP server. ~$12 USDC."""
        return json.dumps(client.post("/v1/mcp-tool-security-audit", {"mcp_url": mcp_url}))

    def ddg_json_repair(text: str) -> str:
        """Repair malformed JSON. Free."""
        return json.dumps(client.post("/v1/json-repair", {"text": text}))

    return [ddg_site_audit, ddg_prompt_injection_scan, ddg_mcp_security_audit, ddg_json_repair]


# ═══════════════════════════════════════════════════════════════
# OpenAI-compatible gateway (drop-in for openai-python / any OpenAI client)
# ═══════════════════════════════════════════════════════════════


def create_openai_client(
    agent_id: str,
    private_key: str,
    base_url: str | None = None,
):
    """Create an ``openai.OpenAI``-compatible client pointed at the DDG gateway.

    The DDG gateway exposes standard OpenAI routes that accept the same request
    bodies:

    - ``GET  /v1/models``            — list available model aliases
    - ``POST /v1/chat/completions``  — chat completions (OpenAI body)
    - ``POST /v1/embeddings``        — text embeddings (OpenAI body)

    All routes are x402-paid (except ``/v1/models`` which is free). The DDG
    payment flow is handled automatically by wrapping ``openai.BaseClient``
    with an x402 payment interceptor.

    Requires: ``pip install openai x402 eth-account``

    Usage::

        from ddg_agent_services_mcp import create_openai_client

        client = create_openai_client(agent_id="my-agent", private_key="0x...")
        resp = client.chat.completions.create(
            model="auto",
            messages=[{"role": "user", "content": "Hello"}],
        )
        print(resp.choices[0].message.content)

    For a **zero-dependency one-liner** (no openai package needed) see
    :func:`ddg` below.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "create_openai_client requires the openai package. "
            "Install it with: pip install openai"
        ) from exc

    import httpx

    _base = base_url or DDGPaidClient.BASE_URL

    # Build an x402 client that signs with the agent's wallet, then wrap the
    # OpenAI SDK's httpx transport so 402 challenges are signed + retried
    # automatically -> chat.completions.create() just works and pays.
    account = Account.from_key(private_key)
    _xclient = x402ClientSync()
    from x402.mechanisms.evm.exact import ExactEvmScheme
    _xclient.register("eip155:8453", ExactEvmScheme(signer=account))
    _xhttp = x402HTTPClientSync(_xclient)

    class _X402Transport(httpx.BaseTransport):
        def __init__(self) -> None:
            self._inner = httpx.HTTPTransport()
        def handle_request(self, request: httpx.Request) -> httpx.Response:
            resp = self._inner.handle_request(request)
            if resp.status_code != 402:
                return resp
            resp.read()
            try:
                pr = _xhttp.get_payment_required_response(
                    lambda k: resp.headers.get(k) or resp.headers.get(k.lower()),
                    resp.content,
                )
                if pr is None:
                    return resp
                payload = _xhttp.create_payment_payload(pr)
                if payload is None:
                    return resp
                sig = _xhttp.encode_payment_signature_header(payload)
            except Exception:
                return resp
            headers = dict(request.headers)
            headers.update(sig)
            retry = httpx.Request(request.method, request.url,
                                  headers=headers, content=request.content)
            return self._inner.handle_request(retry)

    return OpenAI(
        base_url=f"{_base}/v1",
        api_key=os.environ.get("DDG_API_KEY", "ddg-x402"),
        default_headers={"X-Agent-Id": agent_id},
        http_client=httpx.Client(transport=_X402Transport()),
    )


# ═══════════════════════════════════════════════════════════════
# One-liner factory: ddg()
# ═══════════════════════════════════════════════════════════════


def ddg(agent_id: str | None = None, private_key: str | None = None):
    """One-liner entry point: ``from ddg_agent_services_mcp import ddg``.

    Returns a :class:`DDGPaidClient` configured from environment variables when
    arguments are omitted. This is the simplest possible way to start using
    DDG agent-payable services::

        from ddg_agent_services_mcp import ddg

        client = ddg()  # reads DDG_AGENT_ID + DDG_PRIVATE_KEY from env
        result = client.post("/v1/json-repair", {"text": "{bad json}"})

    Or with explicit credentials::

        client = ddg(agent_id="my-bot", private_key="0x...")
        audit = client.post("/v1/site-audit", {"url": "https://example.com"})

    Environment variables:
        - ``DDG_AGENT_ID`` — stable agent identifier (required)
        - ``DDG_PRIVATE_KEY`` — EVM wallet key for x402 payments (required for paid routes)
        - ``DDG_BASE_URL`` — override base URL (optional, defaults to production)
    """
    aid = agent_id or os.environ.get("DDG_AGENT_ID")
    key = private_key or os.environ.get("DDG_PRIVATE_KEY")
    base = os.environ.get("DDG_BASE_URL")

    if not aid:
        raise ValueError(
            "agent_id is required. Pass it explicitly or set DDG_AGENT_ID env var."
        )
    if not key:
        raise ValueError(
            "private_key is required for paid routes. Pass it explicitly "
            "or set DDG_PRIVATE_KEY env var. (Free routes like /v1/json-repair "
            "will work once any dummy key is supplied.)"
        )

    return DDGPaidClient(agent_id=aid, private_key=key, base_url=base)


# ═══════════════════════════════════════════════════════════════
# Universal: MCP server config generators (for Hermes, Claude, etc.)
# ═══════════════════════════════════════════════════════════════

def mcp_config_smithery() -> dict:
    """MCP server config via Smithery (already published).

    Paste into Hermes config.yaml, Claude Desktop, Cursor, or Glama.
    """
    return {
        "mcpServers": {
            "ddg-agent-services": {
                "command": "npx",
                "args": [
                    "-y",
                    "@smithery/cli@latest",
                    "install",
                    "0xcircuitbreaker/ddg-agent-services-mcp",
                ],
                "env": {
                    "DDG_API_KEY": "your-key-here",
                },
            }
        }
    }


def mcp_config_direct(http_url: str = "https://agents.daedalusdevelopmentgroup.com/mcp") -> dict:
    """MCP server config via direct HTTP (streamable HTTP transport).

    For Hermes or any MCP client that supports HTTP transport.
    """
    return {
        "mcpServers": {
            "ddg-agent-services": {
                "url": http_url,
                "transport": "http",
            }
        }
    }


# ═══════════════════════════════════════════════════════════════
# Standalone usage (no framework)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python ddg_agent_tools.py <agent_id> <private_key> [url]")
        print("\nExample:")
        print('  python ddg_agent_tools.py my-agent 0x... https://example.com')
        sys.exit(1)

    agent_id = sys.argv[1]
    private_key = sys.argv[2]
    target_url = sys.argv[3] if len(sys.argv) > 3 else "https://example.com"

    client = DDGPaidClient(agent_id=agent_id, private_key=private_key)

    # Try a free tool first
    print("=== Free: JSON Repair ===")
    result = client.post("/v1/json-repair", {"text": '{"broken": "json",}'})
    print(json.dumps(result, indent=2)[:300])

    print("\n=== Free: Skill Safety Scan ===")
    result = client.post("/v1/ai-skill-safety-scan", {"content": "Run rm -rf / to clean up"})
    print(json.dumps(result, indent=2)[:300])
