#!/usr/bin/env python3
"""DDG Agent Services MCP server skeleton.

Run locally with an MCP-capable client after installing the MCP Python SDK:
    uv run --with mcp python sales_artifacts/agent_payments/mcp/ddg_agent_services_mcp_server.py

This skeleton intentionally proxies only public DDG payment-edge routes and never exposes
provider credentials or private payment material.
"""
from __future__ import annotations

import json
import os
import re
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
    "mcp.daedalusdevelopmentgroup.com",
    "localhost",
    "127.0.0.1",
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
    if parsed.scheme != "https" and host not in {"localhost", "127.0.0.1"}:
        raise SystemExit("Unsafe DDG_AGENT_SERVICES_BASE_URL: non-local DDG MCP base URLs must use HTTPS")
    if host not in _allowed_base_hosts():
        raise SystemExit("Unsafe DDG_AGENT_SERVICES_BASE_URL: host is not in DDG_AGENT_SERVICES_ALLOWED_HOSTS")
    return candidate


BASE_URL = _validated_base_url(os.getenv("DDG_AGENT_SERVICES_BASE_URL", DEFAULT_BASE_URL))
DEFAULT_AGENT_ID = os.getenv("DDG_MCP_AGENT_ID", "ddg-mcp-client")
ALLOWED_EXTRA_HEADERS = {
    "authorization",
    "payment-signature",
    "x-payment",
    "payment-proof",
    "x-direct-crypto-proof",
    "idempotency-key",
}

mcp = FastMCP("ddg-agent-services")


def _safe_path(path: str) -> str:
    candidate = str(path or "").strip()
    if not candidate.startswith("/") or "://" in candidate or ".." in candidate or len(candidate) > 160:
        raise ValueError("unsafe_ddg_path")
    if not re.fullmatch(r"/[A-Za-z0-9_./?=&:%+\-]*", candidate):
        raise ValueError("unsafe_ddg_path")
    return candidate


def _filtered_extra_headers(headers: dict[str, str] | None) -> dict[str, str]:
    safe: dict[str, str] = {}
    for key, value in (headers or {}).items():
        normalized = str(key).strip().lower()
        if normalized not in ALLOWED_EXTRA_HEADERS:
            continue
        text = str(value)
        if "\n" in text or "\r" in text:
            continue
        safe[key] = text[:8192]
    return safe


def _json_request(path: str, *, method: str = "GET", payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
    body = json.dumps(payload).encode() if payload is not None else None
    req_headers = {"accept": "application/json", "x-agent-id": DEFAULT_AGENT_ID}
    if body is not None:
        req_headers["content-type"] = "application/json"
    req_headers.update(_filtered_extra_headers(headers))
    try:
        safe_path = _safe_path(path)
    except ValueError as exc:
        return {"status": 0, "headers": {}, "body": {"error": str(exc)}}
    req = urllib.request.Request(BASE_URL + safe_path, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode(errors="replace")
            return {"status": resp.status, "headers": dict(resp.headers), "body": json.loads(raw) if raw else {}}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"raw": raw[:1000]}
        return {"status": exc.code, "headers": dict(exc.headers), "body": parsed}


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
def ddg_quote_payment(path: str = "/v1/model/chat-completions") -> dict[str, Any]:
    """Return the payment challenge for a DDG protected route without executing backend compute."""
    return _json_request(path, method="POST", payload={"model": "glm-5.2", "messages": [{"role": "user", "content": "quote"}]})


@mcp.tool()
def ddg_run_paid_model(route: str, prompt: str, payment_headers: dict[str, str] | None = None) -> dict[str, Any]:
    """Run a paid model/chat or agent-run route after caller supplies valid payment headers."""
    if route.startswith("kimi-code/") or route.startswith("claude-code/") or route.startswith("ollama/"):
        return _json_request("/v1/model/agent-run", method="POST", payload={"route": route, "task": prompt}, headers=payment_headers or {})
    return _json_request("/v1/model/chat-completions", method="POST", payload={"model": route, "messages": [{"role": "user", "content": prompt}]}, headers=payment_headers or {})


@mcp.tool()
def ddg_submit_order(service_id: str, request: dict[str, Any], payment_headers: dict[str, str] | None = None) -> dict[str, Any]:
    """Submit a paid operator-reviewed DDG order after caller supplies valid payment headers/proof."""
    payload = {"service_id": service_id, **request}
    return _json_request("/v1/order-intake", method="POST", payload=payload, headers=payment_headers or {})


@mcp.tool()
def ddg_request_ollama_model(model: str, reason: str = "requested by agent swarm", expected_size_gb: float | None = None, runtime: str = "ollama") -> dict[str, Any]:
    """Queue a local model/runtime request. This never auto-downloads by public request."""
    payload: dict[str, Any] = {"model": model, "runtime": runtime, "reason": reason}
    if expected_size_gb is not None:
        payload["expected_size_gb"] = expected_size_gb
    return _json_request("/v1/ollama-model-request", method="POST", payload=payload)


@mcp.tool()
def ddg_checkout_conformance() -> dict[str, Any]:
    """Return DDG's public checkout conformance profile without spending money."""
    return _json_request("/.well-known/ddg-agent-checkout-conformance.json")


@mcp.tool()
def ddg_agent_status() -> dict[str, Any]:
    """Return DDG's machine-readable service/rail/MCP status document."""
    return _json_request("/.well-known/ddg-agent-status.json")


@mcp.tool()
def ddg_skill_safety_scan(skill_markdown: str, label: str = "mcp-client-submission") -> dict[str, Any]:
    """Run the free static-only DDG AI skill/workflow safety scan.

    The scan never executes submitted code and redacts secret-like evidence.
    """
    return _json_request(
        "/v1/ai-skill-safety-scan",
        method="POST",
        payload={"label": label, "skill_markdown": str(skill_markdown)[:200000]},
    )


def _safe_order_id(order_id: str) -> str:
    text = str(order_id or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{6,96}", text):
        raise ValueError("unsafe_order_id")
    return text


@mcp.tool()
def ddg_order_status(order_id: str) -> dict[str, Any]:
    """Poll an agent-scoped DDG order status URL."""
    try:
        safe_order_id = _safe_order_id(order_id)
    except ValueError as exc:
        return {"status": 0, "body": {"error": str(exc)}}
    return _json_request(f"/v1/orders/{safe_order_id}")


@mcp.tool()
def ddg_order_artifact(order_id: str) -> dict[str, Any]:
    """Fetch an agent-scoped DDG order artifact when ready."""
    try:
        safe_order_id = _safe_order_id(order_id)
    except ValueError as exc:
        return {"status": 0, "body": {"error": str(exc)}}
    return _json_request(f"/v1/orders/{safe_order_id}/artifact")


@mcp.tool()
def ddg_receipt_verify_design(order_id: str, receipt_hash: str) -> dict[str, Any]:
    """Describe the planned free receipt-verification tool contract.

    This is intentionally marked not-live until `/v1/receipt-verify` is implemented
    and backed by payment-edge audit/state reconciliation.
    """
    return {
        "status": "planned_not_live",
        "planned_endpoint": "/v1/receipt-verify",
        "input": {"order_id": order_id, "receipt_hash": receipt_hash},
        "will_return": ["valid", "service_id", "payment_rail", "amount_usd", "settled_at", "artifact_hash"],
        "privacy": "The verifier should accept hashes/ids only and never return buyer contact, raw payment tokens, or provider metadata.",
    }


@mcp.tool()
def ddg_security_service_catalog() -> dict[str, Any]:
    """Return DDG's AI-agent cybersecurity service catalog."""
    # This file ships with the package; hosted deployments can proxy it as a public well-known asset later.
    here = os.path.dirname(__file__)
    catalog_path = os.path.abspath(os.path.join(here, "..", "cybersecurity-services.json"))
    with open(catalog_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@mcp.tool()
def ddg_tx_smoke_test(payment_headers: dict[str, str] | None = None) -> dict[str, Any]:
    """Exercise the one-cent DDG transaction smoke-test route with caller-supplied payment headers."""
    return _json_request("/v1/tx-smoke-test", method="POST", payload={"request_label": "mcp-tx-smoke"}, headers=payment_headers or {})


if __name__ == "__main__":
    mcp.run()
