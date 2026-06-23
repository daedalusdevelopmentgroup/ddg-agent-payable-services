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

    def read(self, size: int = -1) -> bytes:
        data = json.dumps({"ok": True}).encode()
        return data if size is None or size < 0 else data[:size]


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


class _LargeHTTPResponse(_FakeHTTPResponse):
    def read(self, size: int = -1) -> bytes:
        return b"a" * (server.MAX_RESPONSE_BYTES + 1)


def test_response_size_limit_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server.urllib.request, "urlopen", lambda req, timeout: _LargeHTTPResponse())
    result = server._json_request("/.well-known/ddg-agent-status.json")
    assert result["status"] == 0
    assert result["body"]["error"] == "ddg_response_too_large"


def test_json_response_redacts_sensitive_keys_and_values(monkeypatch: pytest.MonkeyPatch) -> None:
    class SensitiveResponse(_FakeHTTPResponse):
        def read(self, size: int = -1) -> bytes:
            body = {
                "token": "placeholder-token-value",
                "message": "Bearer abcdefghijklmnop",
                "nested": {"safe": "ok"},
            }
            data = json.dumps(body).encode()
            return data if size is None or size < 0 else data[:size]

    monkeypatch.setattr(server.urllib.request, "urlopen", lambda req, timeout: SensitiveResponse())
    result = server._json_request("/.well-known/ddg-agent-status.json")
    assert result["body"]["token"] == "[REDACTED]"
    assert result["body"]["message"] == "[REDACTED]"
    assert result["body"]["nested"]["safe"] == "ok"


def test_json_resource_text_redacts_sensitive_keys_and_values(monkeypatch: pytest.MonkeyPatch) -> None:
    class SensitiveResourceResponse(_FakeHTTPResponse):
        def read(self, size: int = -1) -> bytes:
            body = {
                "ok": True,
                "authorization": "Bearer abcdefghijklmnop",
                "public_note": "this contains Bearer qwertyuiopasdfgh and should be redacted",
            }
            data = json.dumps(body).encode()
            return data if size is None or size < 0 else data[:size]

    monkeypatch.setattr(server.urllib.request, "urlopen", lambda req, timeout: SensitiveResourceResponse())
    text = server.ddg_manifest_status_resource()
    parsed = json.loads(text)
    assert parsed["authorization"] == "[REDACTED]"
    assert parsed["public_note"] == "this contains [REDACTED] and should be redacted"
    assert "qwertyuiopasdfgh" not in text
    assert "sk-proj-" not in text


def test_public_resource_index_and_allowlist() -> None:
    index = server.ddg_public_resource_index()
    assert index["status"] == 200
    uris = {item["uri"] for item in index["resources"]}
    assert "ddg://manifest/status" in uris
    assert "ddg://manifest/refund-policy" in uris

    rejected = server.ddg_fetch_public_resource("https://evil.example/resource")
    assert rejected["status"] == 0
    assert rejected["body"]["error"] == "unsupported_public_resource"


def test_distribution_targets_and_bazaar_readiness_are_gated() -> None:
    distribution = server.ddg_agent_distribution_targets()
    assert distribution["status"] == "active_distribution_work_started"
    target_ids = {target["id"] for target in distribution["targets"]}
    assert "official_mcp_registry" in target_ids
    assert "cdp_x402_bazaar" in target_ids

    bazaar = server.ddg_x402_bazaar_readiness()
    assert bazaar["status"] == "candidate_metadata_ready_not_indexed_until_real_cdp_settlement"
    resources = {item["resource"] for item in bazaar["candidate_resources"]}
    assert "https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test" in resources
    assert any("settlement" in requirement.lower() for requirement in bazaar["indexing_requirements"])


def test_static_distribution_resources_are_json() -> None:
    radar = json.loads(server.ddg_distribution_agent_radar_resource())
    assert radar["mcp_registry"]["registry_name"] == "io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp"

    bazaar = json.loads(server.ddg_distribution_x402_bazaar_readiness_resource())
    assert bazaar["candidate_resources"][0]["service_id"] == "tx_penny_smoke_test"
