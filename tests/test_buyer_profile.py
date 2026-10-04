from __future__ import annotations

import asyncio
import inspect

import pytest

from ddg_agent_services_mcp import server


EXPECTED_TOOLS = {
    "find_services",
    "get_service",
    "call_service",
    "quote_payment",
    "status",
    "order_status",
    "receipt_verify",
    "tine_attest",
}


def _tools():
    return asyncio.run(server.buyer_mcp.list_tools())


def test_default_buyer_profile_has_exactly_eight_tools() -> None:
    tools = _tools()
    assert {tool.name for tool in tools} == EXPECTED_TOOLS
    assert len(tools) == 8


def test_model_facing_schemas_never_accept_keys_or_payment_headers() -> None:
    forbidden = {
        "private_key",
        "wallet_private_key",
        "payment_headers",
        "payment_signature",
        "x_payment",
        "authorization",
    }
    for tool in _tools():
        properties = {name.lower() for name in tool.inputSchema.get("properties", {})}
        assert properties.isdisjoint(forbidden), tool.name
    call = next(tool for tool in _tools() if tool.name == "call_service")
    assert "max_spend_usd" in call.inputSchema["properties"]


def test_annotations_distinguish_reads_calls_and_attestations() -> None:
    tools = {tool.name: tool for tool in _tools()}
    for name in EXPECTED_TOOLS - {"call_service", "tine_attest"}:
        annotations = tools[name].annotations
        assert annotations.readOnlyHint is True
        assert annotations.destructiveHint is False
        assert annotations.idempotentHint is True
        assert annotations.openWorldHint is True

    call = tools["call_service"].annotations
    assert call.readOnlyHint is False
    assert call.destructiveHint is True
    assert call.idempotentHint is False
    assert call.openWorldHint is True
    attest = tools["tine_attest"].annotations
    assert attest.readOnlyHint is True
    assert attest.idempotentHint is False


def test_paid_call_requires_and_enforces_explicit_spend_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    service = {
        "service_id": "paid-demo",
        "availability": "available",
        "price_usd": "0.01",
        "path": "/v1/paid-demo",
        "method": "POST",
    }
    monkeypatch.setattr(server, "_canonical_service", lambda *args: (service, None))
    monkeypatch.delenv("DDG_X402_PRIVATE_KEY", raising=False)
    monkeypatch.setenv("DDG_MCP_TRANSPORT", "streamable-http")
    missing = server.call_service("paid-demo", {})
    assert missing["body"]["error"] == "max_spend_required"
    too_low = server.call_service("paid-demo", {}, max_spend_usd=0.001)
    assert too_low["body"]["error"] == "spend_limit_exceeded"
    invalid = server.call_service("paid-demo", {}, max_spend_usd=float("nan"))
    assert invalid["body"]["error"] == "invalid_max_spend"

    seen = {}

    def fake_request(path, *, method="GET", payload=None, headers=None, agent_id=None):
        seen.update(path=path, method=method, payload=payload, headers=headers, agent_id=agent_id)
        return {"status": 402, "headers": {"Payment-Required": "challenge"}, "body": {"error": "payment_required"}}

    monkeypatch.setattr(server, "_json_request", fake_request)
    challenge = server.call_service("paid-demo", {"input": "safe"}, max_spend_usd=0.01, agent_id="buyer-agent")
    assert challenge["status"] == 402
    assert seen["headers"] is None
    assert seen["payload"] == {"input": "safe"}


def test_service_search_rejects_nonfinite_price_without_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "_json_request", lambda *args, **kwargs: pytest.fail("network should not be called"))
    result = server.find_services("safe objective", maximum_price=float("nan"))
    assert result["body"]["error"] == "invalid_maximum_price"


def test_stdio_signer_uses_official_x402_v2_wrapper_only() -> None:
    from ddg_agent_services_mcp import tools

    source = inspect.getsource(tools.DDGPaidClient)
    assert "x402_requests" in source
    assert "register_exact_evm_client" in source
    assert "_manual_402_handler" not in source
    assert "X-PAYMENT" not in source


def test_framework_factories_expose_code_owned_spend_ceiling() -> None:
    from ddg_agent_services_mcp import tools

    for name in (
        "create_langchain_tools",
        "create_crewai_tools",
        "create_openai_agents_tools",
        "create_autogen_tools",
        "create_pydantic_ai_tools",
        "create_llamaindex_tools",
        "create_google_adk_tools",
    ):
        assert "max_spend_usd" in inspect.signature(getattr(tools, name)).parameters


def test_framework_client_without_cap_stops_at_402_before_signing(monkeypatch: pytest.MonkeyPatch) -> None:
    from ddg_agent_services_mcp import tools

    class PaymentRequired:
        status_code = 402
        text = "payment required"

        @staticmethod
        def json():
            return {"error": "payment_required"}

    monkeypatch.setattr(tools.requests, "post", lambda *args, **kwargs: PaymentRequired())
    client = object.__new__(tools.DDGPaidClient)
    client.agent_id = "test-agent"
    client.base_url = "https://agents.daedalusdevelopmentgroup.com"
    client.x402_client = object()
    assert client.post("/v1/site-audit", {"url": "https://example.com"}) == {
        "error": "max_spend_required",
        "status": 402,
    }
