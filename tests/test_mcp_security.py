from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from ddg_agent_services_mcp import server


class _FakeHTTPResponse:
    status = 200
    headers = {
        "Content-Type": "application/json",
        "Set-Cookie": "secret-session=should-not-leak",
        "Authorization": "Bearer should-not-leak",
        "Payment-Required": "challenge-ok",
        "X-Request-Id": "req-123",
    }

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self) -> bytes:
        return json.dumps({"ok": True}).encode()


def test_authorization_header_is_payment_only() -> None:
    filtered = server._filtered_extra_headers(
        {
            "Authorization": "Bearer github-token-placeholder-not-forwarded",
            "X-Payment": "x402-token",
            "Idempotency-Key": "abc123",
        }
    )
    assert "Authorization" not in filtered
    assert filtered["X-Payment"] == "x402-token"
    assert filtered["Idempotency-Key"] == "abc123"

    filtered_payment = server._filtered_extra_headers({"authorization": "Payment mpp-token"})
    assert filtered_payment == {"Authorization": "Payment mpp-token"}


def test_response_headers_are_allowlisted(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_urlopen(req, timeout):
        captured["headers"] = dict(req.header_items())
        return _FakeHTTPResponse()

    monkeypatch.setattr(server.urllib.request, "urlopen", fake_urlopen)
    result = server._json_request(
        "/.well-known/ddg-agent-status.json",
        headers={"Authorization": "Bearer accidental-secret"},
        agent_id="agent-test-1",
    )

    assert result["status"] == 200
    assert result["headers"] == {
        "Content-Type": "application/json",
        "Payment-Required": "challenge-ok",
        "X-Request-Id": "req-123",
    }
    assert "Authorization" not in captured["headers"]
    assert captured["headers"]["X-agent-id"] == "agent-test-1"


def test_submit_order_service_id_cannot_be_overridden(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = {}

    def fake_json_request(path, *, method="GET", payload=None, headers=None, agent_id=None):
        seen.update(path=path, method=method, payload=payload, headers=headers, agent_id=agent_id)
        return {"status": 402, "body": {"error": "payment_required"}}

    monkeypatch.setattr(server, "_json_request", fake_json_request)
    result = server.ddg_submit_order(
        "real_service",
        {"service_id": "attacker_override", "details": "ok"},
        payment_headers={"Authorization": "Payment token"},
        agent_id="buyer-agent-1",
    )

    assert result["status"] == 402
    assert seen["payload"]["service_id"] == "real_service"
    assert seen["payload"]["details"] == "ok"
    assert seen["agent_id"] == "buyer-agent-1"


def test_quote_path_is_allowlisted(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_json_request(*args, **kwargs):
        nonlocal called
        called = True
        return {"status": 999}

    monkeypatch.setattr(server, "_json_request", fake_json_request)
    result = server.ddg_quote_payment("/admin/debug")
    assert result["status"] == 0
    assert result["body"]["error"] == "unsupported_quote_path"
    assert called is False


def test_payload_size_limit_prevents_large_forward(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_urlopen(req, timeout):
        nonlocal called
        called = True
        return _FakeHTTPResponse()

    monkeypatch.setattr(server.urllib.request, "urlopen", fake_urlopen)
    result = server._json_request("/v1/model/chat-completions", method="POST", payload={"x": "a" * (server.MAX_JSON_PAYLOAD_BYTES + 1)})
    assert result["status"] == 0
    assert result["body"]["error"] == "payload_too_large"
    assert called is False


def test_security_profile_documents_controls() -> None:
    profile = server.ddg_mcp_security_profile()
    assert profile["status"] == "source_hardened_public_remote_pending"
    assert profile["controls"]["authorization_forwarding"].startswith("Payment scheme only")
    assert profile["controls"]["arbitrary_url_fetch"] is False
    assert "mcp.daedalusdevelopmentgroup.com" not in profile["controls"]["base_url_allowlist"]


def test_invalid_agent_id_rejected() -> None:
    result = server.ddg_tx_smoke_test(agent_id="bad\nagent")
    assert result["status"] == 0
    assert result["body"]["error"] == "unsafe_agent_id"
