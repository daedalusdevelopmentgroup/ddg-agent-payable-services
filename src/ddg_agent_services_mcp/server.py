#!/usr/bin/env python3
"""DDG Agent Services MCP server.

Run locally with an MCP-capable client after installing the MCP Python SDK:
    uv run --with mcp python -m ddg_agent_services_mcp

The server intentionally proxies only public DDG payment-edge routes. It never
exposes provider credentials, private payment material, arbitrary shell/file
access, or unrestricted URL fetches.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover - runtime dependency guard
    raise SystemExit("Install the MCP Python SDK first: uv run --with mcp python ...") from exc

DEFAULT_BASE_URL = "https://agents.daedalusdevelopmentgroup.com"
DEFAULT_ALLOWED_BASE_HOSTS = {
    "agents.daedalusdevelopmentgroup.com",
    "api.daedalusdevelopmentgroup.com",
    "localhost",
    "127.0.0.1",
}
MAX_HEADER_VALUE_CHARS = 8192
MAX_RESPONSE_HEADER_VALUE_CHARS = 16384
MAX_JSON_PAYLOAD_BYTES = 256 * 1024
MAX_PROMPT_CHARS = 64_000
MAX_SKILL_SCAN_CHARS = 180_000
SAFE_RESPONSE_HEADERS = {
    "content-type",
    "cache-control",
    "payment-required",
    "www-authenticate",
    "x-request-id",
    "x-idempotent-replay",
    "retry-after",
}
ALLOWED_EXTRA_HEADERS = {
    "authorization": "Authorization",
    "payment-signature": "Payment-Signature",
    "x-payment": "X-Payment",
    "payment-proof": "Payment-Proof",
    "x-direct-crypto-proof": "X-Direct-Crypto-Proof",
    "idempotency-key": "Idempotency-Key",
}
QUOTE_PATHS = {
    "/v1/model/chat-completions",
    "/v1/model/agent-run",
    "/v1/order-intake",
    "/v1/tx-smoke-test",
    "/v1/ai-skill-safety-scan",
    "/v1/ollama-model-request",
}


def _allowed_base_hosts() -> set[str]:
    raw = os.getenv("DDG_AGENT_SERVICES_ALLOWED_HOSTS", "").strip()
    extra = {item.strip().lower() for item in raw.replace("\n", ",").split(",") if item.strip()}
    return DEFAULT_ALLOWED_BASE_HOSTS | extra


def _validated_base_url(raw_url: str) -> str:
    candidate = str(raw_url or DEFAULT_BASE_URL).strip().rstrip("/")
    parsed = urllib.parse.urlparse(candidate)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"https", "http"} or not host:
        raise SystemExit("Unsafe DDG_AGENT_SERVICES_BASE_URL: expected http(s) URL")
    if parsed.username or parsed.password:
        raise SystemExit("Unsafe DDG_AGENT_SERVICES_BASE_URL: credentials in URL are not allowed")
    if parsed.scheme != "https" and host not in {"localhost", "127.0.0.1"}:
        raise SystemExit("Unsafe DDG_AGENT_SERVICES_BASE_URL: non-local DDG MCP base URLs must use HTTPS")
    if host not in _allowed_base_hosts():
        raise SystemExit("Unsafe DDG_AGENT_SERVICES_BASE_URL: host is not in DDG_AGENT_SERVICES_ALLOWED_HOSTS")
    return candidate


BASE_URL = _validated_base_url(os.getenv("DDG_AGENT_SERVICES_BASE_URL", DEFAULT_BASE_URL))
DEFAULT_AGENT_ID = os.getenv("DDG_MCP_AGENT_ID", "ddg-mcp-client")

mcp = FastMCP(
    "ddg-agent-services",
    instructions=(
        "Payment-aware DDG Agent-Payable Services wrapper. Free tools expose discovery/status/conformance; "
        "paid tools return structured 402 challenges unless caller supplies valid payment headers. "
        "Never relay provider credentials, raw payment material, arbitrary URLs, or shell/file access. "
        "For hosted/remote use, pass a stable buyer agent_id tool argument so DDG order and payment scopes "
        "do not collapse into the server default identity."
    ),
    website_url="https://agents.daedalusdevelopmentgroup.com/.well-known/ai",
    host=os.getenv("DDG_MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("DDG_MCP_PORT", "8891")),
    streamable_http_path=os.getenv("DDG_MCP_STREAMABLE_HTTP_PATH", "/mcp"),
    stateless_http=True,
    json_response=True,
)


def _bounded_text(value: Any, max_chars: int) -> str:
    text = str(value or "")
    if "\x00" in text:
        text = text.replace("\x00", "")
    return text[:max_chars]


def _safe_agent_id(agent_id: str | None = None) -> str:
    text = str(agent_id or DEFAULT_AGENT_ID or "ddg-mcp-client").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.:@/+\-]{3,128}", text):
        raise ValueError("unsafe_agent_id")
    return text


def _safe_path(path: str) -> str:
    candidate = str(path or "").strip()
    lowered = candidate.lower()
    if (
        not candidate.startswith("/")
        or "://" in candidate
        or ".." in candidate
        or "%2e" in lowered
        or "%2f" in lowered
        or "%5c" in lowered
        or len(candidate) > 160
    ):
        raise ValueError("unsafe_ddg_path")
    if not re.fullmatch(r"/[A-Za-z0-9_./?=&:%+\-]*", candidate):
        raise ValueError("unsafe_ddg_path")
    return candidate


def _safe_quote_path(path: str) -> str:
    candidate = _safe_path(path)
    path_only = urllib.parse.urlparse(candidate).path
    if path_only not in QUOTE_PATHS:
        raise ValueError("unsupported_quote_path")
    return candidate


def _safe_identifier(value: Any, *, label: str, pattern: str = r"[A-Za-z0-9_.:/@+\-]{1,128}") -> str:
    text = str(value or "").strip()
    if not re.fullmatch(pattern, text):
        raise ValueError(f"unsafe_{label}")
    return text


def _safe_order_id(order_id: str) -> str:
    return _safe_identifier(order_id, label="order_id", pattern=r"[A-Za-z0-9_.:\-]{6,96}")


def _safe_receipt_hash(receipt_hash: str) -> str:
    return _safe_identifier(receipt_hash, label="receipt_hash", pattern=r"[A-Za-z0-9_.:\-]{6,160}")


def _filtered_extra_headers(headers: dict[str, str] | None) -> dict[str, str]:
    """Forward only payment/idempotency headers and never generic credentials.

    In particular, `Authorization` is allowed only for `Payment ...` values.
    This prevents an MCP caller from accidentally relaying unrelated Bearer,
    Basic, GitHub, cloud, or provider tokens to the DDG service endpoint.
    """
    safe: dict[str, str] = {}
    for key, value in (headers or {}).items():
        normalized = str(key).strip().lower()
        canonical = ALLOWED_EXTRA_HEADERS.get(normalized)
        if not canonical:
            continue
        text = str(value or "").strip()
        if "\n" in text or "\r" in text or "\x00" in text:
            continue
        if normalized == "authorization" and not text.lower().startswith("payment "):
            continue
        safe[canonical] = text[:MAX_HEADER_VALUE_CHARS]
    return safe


def _safe_response_headers(headers: Any) -> dict[str, str]:
    public: dict[str, str] = {}
    for key, value in dict(headers or {}).items():
        normalized = str(key).strip().lower()
        if normalized in SAFE_RESPONSE_HEADERS:
            public[str(key)] = str(value)[:MAX_RESPONSE_HEADER_VALUE_CHARS]
    return public


def _json_payload_bytes(payload: dict[str, Any] | None) -> bytes | None:
    if payload is None:
        return None
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(body) > MAX_JSON_PAYLOAD_BYTES:
        raise ValueError("payload_too_large")
    return body


def _json_request(
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    try:
        safe_path = _safe_path(path)
        safe_agent_id = _safe_agent_id(agent_id)
        body = _json_payload_bytes(payload)
    except ValueError as exc:
        return {"status": 0, "headers": {}, "body": {"error": str(exc)}}

    method = method.upper().strip()
    if method not in {"GET", "POST"}:
        return {"status": 0, "headers": {}, "body": {"error": "unsupported_http_method"}}

    req_headers = {"Accept": "application/json", "X-Agent-Id": safe_agent_id}
    if body is not None:
        req_headers["Content-Type"] = "application/json"
    req_headers.update(_filtered_extra_headers(headers))
    req = urllib.request.Request(BASE_URL + safe_path, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode(errors="replace")
            parsed = json.loads(raw) if raw else {}
            return {"status": resp.status, "headers": _safe_response_headers(resp.headers), "body": parsed}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"raw": raw[:500]}
        return {"status": exc.code, "headers": _safe_response_headers(exc.headers), "body": parsed}
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
        return {
            "status": 0,
            "headers": {},
            "body": {"error": "ddg_request_failed", "reason": exc.__class__.__name__},
        }
    except json.JSONDecodeError:
        return {"status": 0, "headers": {}, "body": {"error": "invalid_json_from_ddg"}}


@mcp.tool()
def ddg_mcp_security_profile() -> dict[str, Any]:
    """Return this MCP wrapper's local security controls and publication gates."""
    parsed = urllib.parse.urlparse(BASE_URL)
    return {
        "status": "source_hardened_public_remote_pending",
        "base_url_host": parsed.hostname,
        "transport": {
            "stdio": "ready",
            "streamable_http": "source_ready_local_smoked_public_deploy_pending",
        },
        "controls": {
            "base_url_allowlist": sorted(_allowed_base_hosts()),
            "https_required_for_non_local_upstreams": True,
            "arbitrary_url_fetch": False,
            "shell_or_file_tools": False,
            "payment_header_allowlist": sorted(ALLOWED_EXTRA_HEADERS.values()),
            "authorization_forwarding": "Payment scheme only; Bearer/Basic tokens are dropped",
            "response_header_allowlist": sorted(SAFE_RESPONSE_HEADERS),
            "max_json_payload_bytes": MAX_JSON_PAYLOAD_BYTES,
            "max_prompt_chars": MAX_PROMPT_CHARS,
            "hosted_remote_requires_agent_id_argument": True,
        },
        "publication_gate": "Do not add hosted remotes to mcp/server.json until public endpoint deployment, MCP-client smoke, and leak scan pass.",
    }


@mcp.tool()
def ddg_list_services() -> dict[str, Any]:
    """List DDG live/manual services from the public pricing and catalog surfaces."""
    pricing = _json_request("/.well-known/ddg-agent-pricing.json")
    catalog = _json_request("/.well-known/agent-catalog.json")
    return {"pricing": pricing, "catalog": catalog}


@mcp.tool()
def ddg_list_models() -> dict[str, Any]:
    """List local/free Ollama models and queryable paid/account-backed route labels."""
    ollama = _json_request("/v1/ollama-models")
    catalog = _json_request("/.well-known/agent-catalog.json")
    return {"ollama": ollama, "queryable_model_routes": catalog.get("body", {}).get("queryable_model_routes", [])}


@mcp.tool()
def ddg_list_local_runtime_options() -> dict[str, Any]:
    """List free-seat status plus requestable local runtimes such as Ollama, llama.cpp, LM Studio, OpenAI-compatible servers, and vLLM."""
    catalog = _json_request("/v1/ollama-models")
    body = catalog.get("body", {}) if isinstance(catalog.get("body"), dict) else {}
    return {
        "status": catalog.get("status"),
        "local_free_seats": body.get("local_free_seats"),
        "lease": body.get("lease"),
        "local_runtime_options": body.get("local_runtime_options", []),
        "request_policy": body.get("request_policy", {}),
    }


@mcp.tool()
def ddg_quote_payment(path: str = "/v1/model/chat-completions", agent_id: str | None = None) -> dict[str, Any]:
    """Return the payment challenge for a supported DDG protected route without executing backend compute."""
    try:
        safe_path = _safe_quote_path(path)
    except ValueError as exc:
        return {"status": 0, "headers": {}, "body": {"error": str(exc)}}
    payload: dict[str, Any]
    if safe_path == "/v1/model/agent-run":
        payload = {"route": "kimi-code/k2.7", "task": "quote"}
    elif safe_path == "/v1/order-intake":
        payload = {"service_id": "agent_payment_readiness_audit", "request": {"quote": True}}
    elif safe_path == "/v1/ai-skill-safety-scan":
        payload = {"label": "quote", "skill_markdown": "# quote"}
    elif safe_path == "/v1/ollama-model-request":
        payload = {"model": "llama3.1:8b", "runtime": "ollama", "reason": "quote"}
    else:
        payload = {"model": "glm-5.2", "messages": [{"role": "user", "content": "quote"}]}
    return _json_request(safe_path, method="POST", payload=payload, agent_id=agent_id)


@mcp.tool()
def ddg_run_paid_model(route: str, prompt: str, payment_headers: dict[str, str] | None = None, agent_id: str | None = None) -> dict[str, Any]:
    """Run a paid model/chat or agent-run route after caller supplies valid payment headers."""
    try:
        safe_route = _safe_identifier(route, label="route", pattern=r"[A-Za-z0-9_.:/@+\-]{1,96}")
    except ValueError as exc:
        return {"status": 0, "headers": {}, "body": {"error": str(exc)}}
    safe_prompt = _bounded_text(prompt, MAX_PROMPT_CHARS)
    if safe_route.startswith(("kimi-code/", "claude-code/", "ollama/")):
        return _json_request(
            "/v1/model/agent-run",
            method="POST",
            payload={"route": safe_route, "task": safe_prompt},
            headers=payment_headers or {},
            agent_id=agent_id,
        )
    return _json_request(
        "/v1/model/chat-completions",
        method="POST",
        payload={"model": safe_route, "messages": [{"role": "user", "content": safe_prompt}]},
        headers=payment_headers or {},
        agent_id=agent_id,
    )


@mcp.tool()
def ddg_submit_order(
    service_id: str,
    request: dict[str, Any],
    payment_headers: dict[str, str] | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    """Submit a paid operator-reviewed DDG order after caller supplies valid payment headers/proof."""
    try:
        safe_service_id = _safe_identifier(service_id, label="service_id", pattern=r"[A-Za-z0-9_.:\-]{2,96}")
    except ValueError as exc:
        return {"status": 0, "headers": {}, "body": {"error": str(exc)}}
    if not isinstance(request, dict):
        return {"status": 0, "headers": {}, "body": {"error": "request_must_be_object"}}
    payload = dict(request)
    payload["service_id"] = safe_service_id
    return _json_request("/v1/order-intake", method="POST", payload=payload, headers=payment_headers or {}, agent_id=agent_id)


@mcp.tool()
def ddg_request_ollama_model(
    model: str,
    reason: str = "requested by agent swarm",
    expected_size_gb: float | None = None,
    runtime: str = "ollama",
    agent_id: str | None = None,
) -> dict[str, Any]:
    """Queue a local model/runtime request. This never auto-downloads by public request."""
    try:
        safe_model = _safe_identifier(model, label="model", pattern=r"[A-Za-z0-9_.:/@+\-]{1,128}")
        safe_runtime = _safe_identifier(runtime, label="runtime", pattern=r"[A-Za-z0-9_.:\-]{1,48}")
    except ValueError as exc:
        return {"status": 0, "headers": {}, "body": {"error": str(exc)}}
    payload: dict[str, Any] = {"model": safe_model, "runtime": safe_runtime, "reason": _bounded_text(reason, 2000)}
    if expected_size_gb is not None:
        if expected_size_gb < 0 or expected_size_gb > 2048:
            return {"status": 0, "headers": {}, "body": {"error": "unsafe_expected_size_gb"}}
        payload["expected_size_gb"] = expected_size_gb
    return _json_request("/v1/ollama-model-request", method="POST", payload=payload, agent_id=agent_id)


@mcp.tool()
def ddg_checkout_conformance() -> dict[str, Any]:
    """Return DDG's public checkout conformance profile without spending money."""
    return _json_request("/.well-known/ddg-agent-checkout-conformance.json")


@mcp.tool()
def ddg_agent_status() -> dict[str, Any]:
    """Return DDG's machine-readable service/rail/MCP status document."""
    return _json_request("/.well-known/ddg-agent-status.json")


@mcp.tool()
def ddg_skill_safety_scan(skill_markdown: str, label: str = "mcp-client-submission", agent_id: str | None = None) -> dict[str, Any]:
    """Run the free static-only DDG AI skill/workflow safety scan.

    The scan never executes submitted code and redacts secret-like evidence.
    """
    try:
        safe_label = _safe_identifier(label, label="label", pattern=r"[A-Za-z0-9_.:\-]{1,96}")
    except ValueError as exc:
        return {"status": 0, "headers": {}, "body": {"error": str(exc)}}
    return _json_request(
        "/v1/ai-skill-safety-scan",
        method="POST",
        payload={"label": safe_label, "skill_markdown": _bounded_text(skill_markdown, MAX_SKILL_SCAN_CHARS)},
        agent_id=agent_id,
    )


@mcp.tool()
def ddg_order_status(order_id: str, agent_id: str | None = None) -> dict[str, Any]:
    """Poll an agent-scoped DDG order status URL."""
    try:
        safe_order_id = _safe_order_id(order_id)
    except ValueError as exc:
        return {"status": 0, "body": {"error": str(exc)}}
    return _json_request(f"/v1/orders/{safe_order_id}", agent_id=agent_id)


@mcp.tool()
def ddg_order_artifact(order_id: str, agent_id: str | None = None) -> dict[str, Any]:
    """Fetch an agent-scoped DDG order artifact when ready."""
    try:
        safe_order_id = _safe_order_id(order_id)
    except ValueError as exc:
        return {"status": 0, "body": {"error": str(exc)}}
    return _json_request(f"/v1/orders/{safe_order_id}/artifact", agent_id=agent_id)


@mcp.tool()
def ddg_receipt_verify_design(order_id: str, receipt_hash: str) -> dict[str, Any]:
    """Describe the planned free receipt-verification tool contract.

    This is intentionally marked not-live until `/v1/receipt-verify` is implemented
    and backed by payment-edge audit/state reconciliation.
    """
    try:
        safe_order_id = _safe_order_id(order_id)
        safe_receipt_hash = _safe_receipt_hash(receipt_hash)
    except ValueError as exc:
        return {"status": 0, "body": {"error": str(exc)}}
    return {
        "status": "planned_not_live",
        "planned_endpoint": "/v1/receipt-verify",
        "input": {"order_id": safe_order_id, "receipt_hash": safe_receipt_hash},
        "will_return": ["valid", "service_id", "payment_rail", "amount_usd", "settled_at", "artifact_hash"],
        "privacy": "The verifier should accept hashes/ids only and never return buyer contact, raw payment tokens, or provider metadata.",
    }


@mcp.tool()
def ddg_security_service_catalog() -> dict[str, Any]:
    """Return DDG's AI-agent cybersecurity service catalog."""
    return _json_request("/.well-known/ddg-cybersecurity-services.json")


@mcp.tool()
def ddg_tx_smoke_test(payment_headers: dict[str, str] | None = None, agent_id: str | None = None) -> dict[str, Any]:
    """Exercise the one-cent DDG transaction smoke-test route with caller-supplied payment headers."""
    return _json_request(
        "/v1/tx-smoke-test",
        method="POST",
        payload={"request_label": "mcp-tx-smoke"},
        headers=payment_headers or {},
        agent_id=agent_id,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="DDG Agent-Payable Services MCP server")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http", "sse"),
        default=os.getenv("DDG_MCP_TRANSPORT", "stdio"),
        help="MCP transport. Use streamable-http for hosted/remote MCP.",
    )
    parser.add_argument(
        "--mount-path",
        default=os.getenv("DDG_MCP_MOUNT_PATH") or None,
        help="Optional ASGI mount path override for HTTP transports.",
    )
    args = parser.parse_args()
    mcp.run(transport=args.transport, mount_path=args.mount_path)


if __name__ == "__main__":
    main()
