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
from collections.abc import Mapping
import ipaddress
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
    from mcp.server.transport_security import TransportSecuritySettings
except Exception as exc:  # pragma: no cover - runtime dependency guard
    raise SystemExit("Install the MCP Python SDK first: uv run --with mcp python ...") from exc

DEFAULT_BASE_URL = "https://agents.daedalusdevelopmentgroup.com"
DEFAULT_ALLOWED_BASE_HOSTS = {
    "agents.daedalusdevelopmentgroup.com",
    "api.daedalusdevelopmentgroup.com",
}
LOCAL_ALLOWED_BASE_HOSTS = {"localhost", "127.0.0.1"}
MAX_HEADER_VALUE_CHARS = 8192
MAX_RESPONSE_HEADER_VALUE_CHARS = 16384
MAX_RESPONSE_BYTES = 768 * 1024
MAX_RESOURCE_TEXT_CHARS = 384 * 1024
MAX_JSON_PAYLOAD_BYTES = 256 * 1024
MAX_PROMPT_CHARS = 64_000
MAX_SKILL_SCAN_CHARS = 180_000
SENSITIVE_KEY_RE = re.compile(r"(?i)(authorization|cookie|secret|token|password|private[_-]?key|seed|mnemonic|payment[_-]?proof|raw[_-]?payment|provider[_-]?metadata)")
SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.I | re.S),
    re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{16,}\b"),
    re.compile(r"\bglpat-[A-Za-z0-9_\-]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{16,}\b"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{16,}\b"),
    re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}\b"),
    re.compile(r"\bya29\.[0-9A-Za-z_\-]{20,}\b"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{16,}"),
)
SAFE_RESPONSE_HEADERS = {
    "content-type",
    "cache-control",
    "payment-required",
    "x-payment-required",
    "x-payment-required-v1",
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
PUBLIC_RESOURCE_SPECS: dict[str, dict[str, str]] = {
    "manifest.ai": {"uri": "ddg://manifest/ai", "path": "/.well-known/ai", "mime_type": "application/json", "title": "DDG AI manifest"},
    "manifest.status": {"uri": "ddg://manifest/status", "path": "/.well-known/ddg-agent-status.json", "mime_type": "application/json", "title": "DDG agent status"},
    "manifest.catalog": {"uri": "ddg://manifest/catalog", "path": "/.well-known/agent-catalog.json", "mime_type": "application/json", "title": "DDG service catalog"},
    "manifest.pricing": {"uri": "ddg://manifest/pricing", "path": "/.well-known/ddg-agent-pricing.json", "mime_type": "application/json", "title": "DDG agent pricing"},
    "manifest.checkout_conformance": {"uri": "ddg://manifest/checkout-conformance", "path": "/.well-known/ddg-agent-checkout-conformance.json", "mime_type": "application/json", "title": "DDG checkout conformance"},
    "manifest.refund_policy": {"uri": "ddg://manifest/refund-policy", "path": "/.well-known/ddg-agent-refund-policy.json", "mime_type": "application/json", "title": "DDG strict refund/reversal policy"},
    "manifest.cybersecurity_services": {"uri": "ddg://manifest/cybersecurity-services", "path": "/.well-known/ddg-cybersecurity-services.json", "mime_type": "application/json", "title": "DDG cybersecurity services"},
    "docs.llms": {"uri": "ddg://docs/llms", "path": "/llms.txt", "mime_type": "text/plain", "title": "DDG llms.txt"},
    "docs.mcp_design": {"uri": "ddg://docs/mcp-design", "path": "/.well-known/ddg-agent-swarm-mcp-design.md", "mime_type": "text/markdown", "title": "DDG MCP design"},
    "openapi": {"uri": "ddg://openapi", "path": "/openapi.json", "mime_type": "application/json", "title": "DDG OpenAPI"},
}

DISTRIBUTION_TARGETS: tuple[dict[str, Any], ...] = (
    {
        "id": "owned_agent_discovery_surfaces",
        "name": "Owned machine-readable DDG discovery surfaces",
        "status": "live_and_indexable",
        "kind": "owned_web",
        "priority": "p0",
        "urls": [
            "https://agents.daedalusdevelopmentgroup.com/.well-known/ai",
            "https://agents.daedalusdevelopmentgroup.com/llms.txt",
            "https://agents.daedalusdevelopmentgroup.com/openapi.json",
            "https://agents.daedalusdevelopmentgroup.com/.well-known/agent-catalog.json",
            "https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json",
            "https://agents.daedalusdevelopmentgroup.com/.well-known/agent-skills/index.json",
        ],
        "agent_queries": [
            "x402 checkout conformance service",
            "MCP tool security audit service",
            "agent discovery repair pack",
            "buyer agent smoke probe",
        ],
        "next_action": "Keep public endpoint leak scans and payment-ladder smokes green after every catalog/docs update.",
    },
    {
        "id": "github_public_repo",
        "name": "GitHub public repo and topic search",
        "status": "live",
        "kind": "source_repository",
        "priority": "p0",
        "urls": ["https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services"],
        "agent_queries": ["site:github.com MCP x402 agent commerce", "DDG Agent-Payable Services"],
        "next_action": "Keep CodeQL, CI, Dependabot, security policy, clean commits, and topic metadata green.",
    },
    {
        "id": "official_mcp_registry",
        "name": "Official MCP Registry",
        "status": "public_streamable_http_live_registry_submission_ready",
        "kind": "mcp_registry",
        "priority": "p0",
        "urls": [
            "https://modelcontextprotocol.io/registry/about",
            "https://github.com/modelcontextprotocol/registry",
        ],
        "next_action": "Publish the stdio package to PyPI or deploy/smoke the public Streamable HTTP endpoint, then publish mcp/server.json with mcp-publisher.",
        "do_not_claim_until": [
            "PyPI package exists or public remote MCP endpoint is reachable",
            "registry server.json validation passes",
            "namespace verification/publisher auth succeeds",
        ],
    },
    {
        "id": "cdp_x402_bazaar",
        "name": "CDP x402 Bazaar discovery layer",
        "status": "candidate_metadata_ready_not_indexed_until_real_cdp_settlement",
        "kind": "x402_discovery",
        "priority": "p0",
        "urls": [
            "https://docs.cdp.coinbase.com/x402/bazaar",
            "https://api.cdp.coinbase.com/platform/v2/x402/discovery/search",
            "https://api.cdp.coinbase.com/platform/v2/x402/discovery/mcp",
        ],
        "next_action": "Wire Bazaar discovery extensions into the CDP Facilitator settle flow and complete one real penny-scale settlement with paymentPayload.resource set.",
        "do_not_claim_until": [
            "CDP settle, not verify-only, completes",
            "EXTENSION-RESPONSES does not reject Bazaar metadata",
            "Discovery search or Bazaar MCP returns the DDG resource",
        ],
    },
    {
        "id": "x402scan",
        "name": "x402scan resource directory",
        "status": "registered_live_5_resources",
        "kind": "x402_directory",
        "priority": "p1",
        "urls": [
            "https://www.x402scan.com/server/c3540307-0eb2-455d-90b6-a21f7d5a3792",
            "https://tryponcho.com/m/agents.daedalusdevelopmentgroup.com",
            "https://www.x402scan.com/resources/register",
        ],
        "next_action": "Keep x402scan batch tests green after every OpenAPI/payment-edge update; expand listing copy only after CDP Bazaar settlement indexing is live.",
    },
    {
        "id": "x402_ecosystem_and_awesome_lists",
        "name": "x402 ecosystem pages and awesome lists",
        "status": "listing_packet_ready_after_x402scan_registration",
        "kind": "x402_ecosystem",
        "priority": "p1",
        "urls": ["https://www.x402.org/ecosystem", "https://github.com/xpaysh/awesome-x402"],
        "packet": "submissions/x402-ecosystem/awesome-x402-listing.md",
        "next_action": "Open a listing request/PR now that x402scan and agentcash probes report valid paid resources; keep the submission clear that CDP Bazaar indexing is still settlement-gated.",
    },
    {
        "id": "mcp_aggregators",
        "name": "MCP aggregators and directories",
        "status": "ready_after_public_mcp_endpoint_smoke",
        "kind": "mcp_directory",
        "priority": "p2",
        "urls": ["https://smithery.ai/servers", "https://glama.ai/mcp/servers", "https://mcp.so/"],
        "next_action": "Submit after official MCP Registry/PyPI or public remote MCP endpoint is live to avoid overclaiming installability.",
    },
)

X402_BAZAAR_READINESS: dict[str, Any] = {
    "status": "runtime_bazaar_schemas_live_not_indexed_until_real_cdp_settlement",
    "source_docs_checked": [
        "https://docs.cdp.coinbase.com/x402/bazaar",
        "https://docs.cdp.coinbase.com/x402/quickstart-for-sellers",
    ],
    "indexing_requirements": [
        "Use the CDP Facilitator v2 verify/settle endpoint for production x402 payments.",
        "Attach Bazaar discovery metadata with strict input/output JSON Schemas in route config.",
        "Ensure the settle call includes paymentPayload.resource for the exact payable resource URL.",
        "Complete at least one successful settlement; verify-only does not index resources.",
        "Inspect EXTENSION-RESPONSES for rejected/processing and log only redacted status.",
        "Query discovery search/resources or the Bazaar MCP endpoint after the indexing delay.",
    ],
    "candidate_resources": [
        {
            "service_id": "tx_penny_smoke_test",
            "method": "POST",
            "resource": "https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test",
            "price_usd": "0.01",
            "description": "One-cent side-effect-free x402 transaction smoke test for buyer agents.",
            "input": {"request_label": "buyer-agent-smoke"},
            "inputSchema": {
                "type": "object",
                "properties": {"request_label": {"type": "string", "maxLength": 120}},
                "additionalProperties": False,
            },
            "output": {
                "example": {"ok": True, "service": "tx_penny_smoke_test", "payment": {"protocol": "x402", "receipt": "..."}},
                "schema": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "service": {"const": "tx_penny_smoke_test"},
                        "amount_usd": {"type": "string"},
                        "payment": {"type": "object"},
                    },
                    "required": ["ok", "service", "payment"],
                },
            },
        },
        {
            "service_id": "buyer_agent_smoke_probe",
            "method": "POST",
            "resource": "https://agents.daedalusdevelopmentgroup.com/v1/order-intake",
            "price_usd": "service_catalog_price",
            "description": "Operator-reviewed buyer-agent smoke probe and proof bundle for agent-facing services.",
            "input": {"service_id": "buyer_agent_smoke_probe", "request": {"target": "https://example.com"}},
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service_id": {"const": "buyer_agent_smoke_probe"},
                    "request": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "format": "uri"},
                            "notes": {"type": "string", "maxLength": 2000},
                        },
                        "required": ["target"],
                    },
                },
                "required": ["service_id", "request"],
            },
            "output": {
                "example": {"ok": True, "status": "queued", "order_id": "ord_...", "status_url": "/v1/orders/..."},
                "schema": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "status": {"type": "string"},
                        "order_id": {"type": "string"},
                    },
                },
            },
        },
    ],
    "discovery_verification": [
        "GET https://api.cdp.coinbase.com/platform/v2/x402/discovery/search?query=DDG%20agent%20payment&limit=20",
        "GET https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources?limit=100",
        "Connect an MCP client to https://api.cdp.coinbase.com/platform/v2/x402/discovery/mcp and search for DDG after settlement.",
    ],
}

MCP_REGISTRY_READINESS: dict[str, Any] = {
    "status": "public_streamable_http_live_registry_submission_ready",
    "server_json": "mcp/server.json",
    "registry_name": "io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp",
    "package_identifier": "ddg-agent-services-mcp",
    "public_repo": "https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services",
    "submission_gate": [
        "Stdio package must be available from a public supported package registry such as PyPI, or remote MCP endpoint must be public and smoked.",
        "https://mcp.daedalusdevelopmentgroup.com/mcp is live and MCP-client smoked; keep registry validation/publisher flow green before external MCP directory publication.",
        "Run registry server.json validation before publishing.",
    ],
}

X402_CHAIN_SUPPORT: dict[str, Any] = {
    "status": "multi_chain_x402_live_base_mainnet_direct_crypto_13_assets",
    "x402_enforcement_network": "eip155:8453",
    "x402_accepts_networks": [
        {"network": "eip155:8453", "label": "Base mainnet", "asset": "USDC", "asset_contract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"},
        {"network": "eip155:137", "label": "Polygon mainnet", "asset": "USDC", "asset_contract": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"},
        {"network": "eip155:42161", "label": "Arbitrum One", "asset": "USDC", "asset_contract": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"},
        {"network": "eip155:480", "label": "World Chain mainnet", "asset": "USDC", "asset_contract": "0x79A02482A880bCE3F13e09Da970dC34db4CD24d1"},
        {"network": "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp", "label": "Solana mainnet", "asset": "USDC", "asset_contract": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},
    ],
    "direct_crypto_assets": [
        {"asset": "EVM", "description": "ETH, stablecoins, and EVM-native assets across Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche, BSC, Linea, Scroll, zkSync"},
        {"asset": "BTC"},
        {"asset": "BCH"},
        {"asset": "LTC"},
        {"asset": "DOGE"},
        {"asset": "SOL"},
        {"asset": "TRX"},
        {"asset": "XRP"},
        {"asset": "DOT"},
        {"asset": "XLM"},
        {"asset": "ALGO"},
        {"asset": "ZEC"},
        {"asset": "XMR"},
    ],
    "note": "x402 production settlement currently uses Base mainnet USDC. The payment edge advertises all supported networks in the x402 accepts[] array so AI agents can pay on their preferred chain. Direct-crypto manual/beta supports the 13 public receiving-address families in /.well-known/ddg-direct-crypto-addresses.json; ADA/Cardano is not advertised until a DDG-controlled receiving address and verification/manual-confirmation policy are installed.",
}

X402SCAN_STATUS: dict[str, Any] = {
    "status": "registered_live_5_resources",
    "registered_origin": "https://agents.daedalusdevelopmentgroup.com",
    "server_page": "https://www.x402scan.com/server/c3540307-0eb2-455d-90b6-a21f7d5a3792",
    "merchant_page": "https://tryponcho.com/m/agents.daedalusdevelopmentgroup.com",
    "validated_resources": [
        "https://agents.daedalusdevelopmentgroup.com/v1/site-audit",
        "https://agents.daedalusdevelopmentgroup.com/v1/model/chat-completions",
        "https://agents.daedalusdevelopmentgroup.com/v1/model/agent-run",
        "https://agents.daedalusdevelopmentgroup.com/v1/order-intake",
        "https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test",
    ],
    "latest_batch_test": {
        "result": "5_success_0_failed",
        "network": "eip155:8453",
        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "input_output_schema_warnings": "clean_after_runtime_extensions_bazaar_schema",
    },
    "guardrails": [
        "Directory probes return canonical x402 v2 402 bodies/headers without executing backend compute.",
        "Real work-attempt POSTs without stable AI-agent identity still fail as 403 agent_only.",
        "CDP Bazaar remains separate and is not claimed indexed until real CDP settlement appears in discovery search/MCP.",
    ],
}


def _local_base_urls_enabled() -> bool:
    return os.getenv("DDG_AGENT_SERVICES_ALLOW_LOCAL_BASE_URLS", "").strip().lower() in {"1", "true", "yes", "on"}


def _allowed_base_hosts() -> set[str]:
    raw = os.getenv("DDG_AGENT_SERVICES_ALLOWED_HOSTS", "").strip()
    extra = {item.strip().lower() for item in raw.replace("\n", ",").split(",") if item.strip()}
    allowed = DEFAULT_ALLOWED_BASE_HOSTS | extra
    if _local_base_urls_enabled():
        allowed |= LOCAL_ALLOWED_BASE_HOSTS
    return allowed


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
    # SSRF guard: reject raw-IP literals that resolve to private/link-local/loopback ranges.
    try:
        ip_obj = ipaddress.ip_address(host)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            if host not in {"127.0.0.1"}:
                raise SystemExit(
                    "Unsafe DDG_AGENT_SERVICES_BASE_URL: private/loopback IP literal is not allowed; "
                    "set DDG_AGENT_SERVICES_ALLOW_LOCAL_BASE_URLS=1 only for local development"
                )
    except ValueError:
        pass  # hostname is not an IP literal — fine, proceed to allowlist check
    if host not in _allowed_base_hosts():
        if host in LOCAL_ALLOWED_BASE_HOSTS:
            raise SystemExit(
                "Unsafe DDG_AGENT_SERVICES_BASE_URL: local base URLs require "
                "DDG_AGENT_SERVICES_ALLOW_LOCAL_BASE_URLS=1"
            )
        raise SystemExit("Unsafe DDG_AGENT_SERVICES_BASE_URL: host is not in DDG_AGENT_SERVICES_ALLOWED_HOSTS")
    return candidate


BASE_URL = _validated_base_url(os.getenv("DDG_AGENT_SERVICES_BASE_URL", DEFAULT_BASE_URL))
DEFAULT_AGENT_ID = os.getenv("DDG_MCP_AGENT_ID", "ddg-mcp-client")


def _mcp_allowed_hosts() -> list[str]:
    """Hosts accepted by MCP HTTP DNS-rebinding protection.

    The MCP SDK correctly rejects unknown Host headers. Hosted Cloudflare Tunnel
    traffic arrives with `Host: mcp.daedalusdevelopmentgroup.com`, while local
    smokes use loopback with or without the port. Keep this explicit rather than
    disabling DNS-rebinding protection.
    """
    configured = [part.strip() for part in os.getenv("DDG_MCP_ALLOWED_HOSTS", "").split(",") if part.strip()]
    defaults = [
        "127.0.0.1",
        "127.0.0.1:8891",
        "localhost",
        "localhost:8891",
        "mcp.daedalusdevelopmentgroup.com",
        "agents.daedalusdevelopmentgroup.com",
    ]
    return list(dict.fromkeys(configured + defaults))

mcp = FastMCP(
    "ddg-agent-services",
    instructions=(
        "Payment-aware DDG Agent-Payable Services wrapper. Free tools expose discovery/status/conformance; "
        "paid tools return structured 402 challenges unless caller supplies valid payment headers. "
        "MCP resources expose only allowlisted public DDG manifests/docs. "
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
    transport_security=TransportSecuritySettings(allowed_hosts=_mcp_allowed_hosts()),
)


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Disable urllib's default redirect following so BASE_URL stays authoritative."""

    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


_NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirectHandler)


def _open_no_redirect(req: urllib.request.Request, *, timeout: int = 30) -> Any:
    return _NO_REDIRECT_OPENER.open(req, timeout=timeout)


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


def _filtered_extra_headers(headers: Mapping[str, Any] | None) -> dict[str, str]:
    """Forward only payment/idempotency headers and never generic credentials.

    In particular, `Authorization` is allowed only for `Payment ...` values.
    This prevents an MCP caller from accidentally relaying unrelated Bearer,
    Basic, GitHub, cloud, or provider tokens to the DDG service endpoint.
    """
    if headers is None:
        return {}
    if not isinstance(headers, Mapping):
        raise ValueError("unsafe_payment_headers")
    safe: dict[str, str] = {}
    for key, value in headers.items():
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


def _read_limited_response(resp: Any) -> str:
    raw = resp.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("ddg_response_too_large")
    return raw.decode("utf-8", errors="replace")


def _redact_text(value: str) -> str:
    redacted = value
    for pattern in SENSITIVE_VALUE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _redacted_json(value: Any, *, depth: int = 0) -> Any:
    if depth > 12:
        return "[REDACTED:max-depth]"
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            text_key = str(key)
            if SENSITIVE_KEY_RE.search(text_key):
                safe[text_key] = "[REDACTED]"
            else:
                safe[text_key] = _redacted_json(item, depth=depth + 1)
        return safe
    if isinstance(value, list):
        return [_redacted_json(item, depth=depth + 1) for item in value[:500]]
    if isinstance(value, str):
        return _redact_text(value)[:MAX_RESOURCE_TEXT_CHARS]
    return value


def _static_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(_redacted_json(payload), ensure_ascii=False, indent=2, sort_keys=True)[:MAX_RESOURCE_TEXT_CHARS]


def _parse_json_response(raw: str) -> Any:
    parsed = json.loads(raw) if raw else {}
    return _redacted_json(parsed)


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
    headers: Mapping[str, Any] | None = None,
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
    try:
        extra_headers = _filtered_extra_headers(headers)
    except ValueError as exc:
        return {"status": 0, "headers": {}, "body": {"error": str(exc)}}
    req_headers.update(extra_headers)
    req = urllib.request.Request(BASE_URL + safe_path, data=body, headers=req_headers, method=method)
    try:
        with _open_no_redirect(req, timeout=30) as resp:
            raw = _read_limited_response(resp)
            return {"status": resp.status, "headers": _safe_response_headers(resp.headers), "body": _parse_json_response(raw)}
    except urllib.error.HTTPError as exc:
        raw = exc.read(MAX_RESPONSE_BYTES + 1).decode("utf-8", errors="replace")
        if len(raw) > MAX_RESPONSE_BYTES:
            return {"status": exc.code, "headers": _safe_response_headers(exc.headers), "body": {"error": "ddg_response_too_large"}}
        try:
            parsed = _parse_json_response(raw)
        except Exception:
            parsed = {"error": "non_json_response_from_ddg"}
        return {"status": exc.code, "headers": _safe_response_headers(exc.headers), "body": parsed}
    except ValueError as exc:
        return {"status": 0, "headers": {}, "body": {"error": str(exc)}}
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
        return {
            "status": 0,
            "headers": {},
            "body": {"error": "ddg_request_failed", "reason": exc.__class__.__name__},
        }
    except json.JSONDecodeError:
        return {"status": 0, "headers": {}, "body": {"error": "invalid_json_from_ddg"}}


def _public_resource_spec(resource_id_or_uri: str) -> dict[str, str]:
    key = str(resource_id_or_uri or "").strip()
    if key in PUBLIC_RESOURCE_SPECS:
        return PUBLIC_RESOURCE_SPECS[key]
    for spec in PUBLIC_RESOURCE_SPECS.values():
        if key == spec["uri"]:
            return spec
    raise ValueError("unsupported_public_resource")


def _resource_text(resource_id_or_uri: str) -> str:
    spec = _public_resource_spec(resource_id_or_uri)
    safe_path = _safe_path(spec["path"])
    req = urllib.request.Request(BASE_URL + safe_path, headers={"Accept": spec["mime_type"], "X-Agent-Id": _safe_agent_id()})
    try:
        with _open_no_redirect(req, timeout=30) as resp:
            text = _read_limited_response(resp)
    except urllib.error.HTTPError as exc:
        text = exc.read(MAX_RESPONSE_BYTES + 1).decode("utf-8", errors="replace")
        if len(text) > MAX_RESPONSE_BYTES:
            raise ValueError("ddg_response_too_large") from exc
    if spec["mime_type"] == "application/json":
        try:
            parsed = json.loads(text)
            return json.dumps(_redacted_json(parsed), ensure_ascii=False, indent=2, sort_keys=True)[:MAX_RESOURCE_TEXT_CHARS]
        except json.JSONDecodeError:
            return _static_json_text({"error": "invalid_json_from_ddg", "resource": spec["uri"]})
    return _redact_text(text)[:MAX_RESOURCE_TEXT_CHARS]


def _resource_payload(resource_id_or_uri: str) -> dict[str, Any]:
    try:
        spec = _public_resource_spec(resource_id_or_uri)
        text = _resource_text(spec["uri"])
    except (ValueError, urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
        return {"status": 0, "body": {"error": str(exc)}}
    payload: dict[str, Any] = {
        "status": 200,
        "resource": {k: spec[k] for k in ("uri", "path", "mime_type", "title")},
        "text": text,
        "bytes": len(text.encode("utf-8")),
        "truncated": len(text) >= MAX_RESOURCE_TEXT_CHARS,
    }
    if spec["mime_type"] == "application/json":
        try:
            payload["json"] = _redacted_json(json.loads(text))
            payload.pop("text", None)
        except json.JSONDecodeError:
            payload["json_error"] = "invalid_json_from_ddg"
    return payload


def _public_resource_index() -> list[dict[str, str]]:
    return [
        {"id": key, "uri": spec["uri"], "path": spec["path"], "mime_type": spec["mime_type"], "title": spec["title"]}
        for key, spec in sorted(PUBLIC_RESOURCE_SPECS.items())
    ]


@mcp.tool()
def ddg_mcp_security_profile() -> dict[str, Any]:
    """Return this MCP wrapper's local security controls and publication gates."""
    parsed = urllib.parse.urlparse(BASE_URL)
    return {
        "status": "source_hardened_public_remote_live",
        "base_url_host": parsed.hostname,
        "transport": {
            "stdio": "ready",
            "streamable_http": "public_live_at_https://mcp.daedalusdevelopmentgroup.com/mcp",
        },
        "controls": {
            "base_url_allowlist": sorted(_allowed_base_hosts()),
            "https_required_for_non_local_upstreams": True,
            "local_base_urls_opt_in": _local_base_urls_enabled(),
            "arbitrary_url_fetch": False,
            "shell_or_file_tools": False,
            "payment_header_allowlist": sorted(ALLOWED_EXTRA_HEADERS.values()),
            "authorization_forwarding": "Payment scheme only; Bearer/Basic tokens are dropped",
            "response_header_allowlist": sorted(SAFE_RESPONSE_HEADERS),
            "response_body_redaction": True,
            "max_response_bytes": MAX_RESPONSE_BYTES,
            "max_resource_text_chars": MAX_RESOURCE_TEXT_CHARS,
            "max_json_payload_bytes": MAX_JSON_PAYLOAD_BYTES,
            "max_prompt_chars": MAX_PROMPT_CHARS,
            "public_resource_count": len(PUBLIC_RESOURCE_SPECS),
            "hosted_remote_requires_agent_id_argument": True,
        },
        "publication_gate": "Hosted endpoint deployment and MCP-client smoke have passed; continue to run leak scan plus registry validation/publisher flow before external MCP directory submissions.",
    }


@mcp.tool()
def ddg_public_resource_index() -> dict[str, Any]:
    """List allowlisted DDG public manifests/docs available as MCP resources."""
    return {
        "status": 200,
        "resources": _public_resource_index(),
        "security": "Only fixed DDG public resources are exposed; arbitrary URLs and paths are rejected.",
    }


@mcp.tool()
def ddg_fetch_public_resource(resource: str) -> dict[str, Any]:
    """Fetch an allowlisted DDG public manifest/doc by id or ddg:// URI with redaction and size caps."""
    return _resource_payload(resource)


@mcp.tool()
def ddg_agent_distribution_targets() -> dict[str, Any]:
    """Return the AI-agent radar surfaces DDG is targeting and their current go-live gates."""
    return {
        "status": "active_distribution_work_started",
        "base_url": BASE_URL,
        "targets": list(DISTRIBUTION_TARGETS),
        "security_gate": "Keep source/public/GitHub audits green before every external listing or registry submission.",
        "mcp_registry": MCP_REGISTRY_READINESS,
        "x402_bazaar": {
            "status": X402_BAZAAR_READINESS["status"],
            "candidate_resource_count": len(X402_BAZAAR_READINESS["candidate_resources"]),
        },
    }


@mcp.tool()
def ddg_x402_bazaar_readiness() -> dict[str, Any]:
    """Return CDP x402 Bazaar candidate resources, schema metadata, and settlement indexing gates."""
    return X402_BAZAAR_READINESS


@mcp.tool()
def ddg_x402scan_status() -> dict[str, Any]:
    """Return DDG's x402scan registration status, resource URLs, and runtime probe guardrails."""
    return X402SCAN_STATUS


@mcp.tool()
def ddg_x402_supported_chains() -> dict[str, Any]:
    """Return all x402/direct-crypto chains DDG supports for AI-agent payment routing."""
    return X402_CHAIN_SUPPORT


@mcp.tool()
def ddg_direct_crypto_addresses() -> dict[str, Any]:
    """Return DDG's public direct-crypto receiving addresses for manual/beta payment routing."""
    return _json_request("/.well-known/ddg-direct-crypto-addresses.json")


@mcp.tool()
def ddg_micro_swarm_preview(prompt: str, model: str | None = None, combo: str | None = None, agent_id: str | None = None) -> dict[str, Any]:
    """Run the free DDG micro-model-swarm preview with a local Ollama mini-model."""
    payload: dict[str, Any] = {"prompt": _bounded_text(prompt, MAX_PROMPT_CHARS)}
    if model:
        payload["model"] = _safe_identifier(model, label="model", pattern=r"[A-Za-z0-9_.:/@+\-]{1,128}")
    elif combo:
        payload["combo"] = _safe_identifier(combo, label="combo", pattern=r"[A-Za-z0-9_]{1,64}")
    return _json_request("/v1/micro-model-swarm-preview", method="POST", payload=payload, agent_id=agent_id)


@mcp.tool()
def ddg_ethereum_rpc_query(body: dict[str, Any], agent_id: str | None = None) -> dict[str, Any]:
    """Proxy a free read-only Ethereum JSON-RPC query through DDG's private Reth node (sync-gated)."""
    if not isinstance(body, dict):
        return {"status": 0, "body": {"error": "body_must_be_object"}}
    return _json_request("/v1/ethereum/rpc", method="POST", payload=body, agent_id=agent_id)


@mcp.resource("ddg://distribution/agent-radar", name="ddg_distribution_agent_radar", mime_type="application/json")
def ddg_distribution_agent_radar_resource() -> str:
    """DDG AI-agent distribution targets and go-live gates."""
    return _static_json_text(ddg_agent_distribution_targets())


@mcp.resource("ddg://distribution/x402-bazaar-readiness", name="ddg_distribution_x402_bazaar_readiness", mime_type="application/json")
def ddg_distribution_x402_bazaar_readiness_resource() -> str:
    """DDG x402 Bazaar readiness and candidate resource metadata."""
    return _static_json_text(X402_BAZAAR_READINESS)


@mcp.resource("ddg://distribution/x402scan-status", name="ddg_distribution_x402scan_status", mime_type="application/json")
def ddg_distribution_x402scan_status_resource() -> str:
    """DDG x402scan registration status and validated resource list."""
    return _static_json_text(X402SCAN_STATUS)


@mcp.resource("ddg://distribution/x402-chains", name="ddg_distribution_x402_chains", mime_type="application/json")
def ddg_distribution_x402_chains_resource() -> str:
    """DDG supported x402/direct-crypto chains and assets."""
    return _static_json_text(X402_CHAIN_SUPPORT)


@mcp.resource("ddg://manifest/ai", name="ddg_manifest_ai", mime_type="application/json")
def ddg_manifest_ai_resource() -> str:
    """DDG public AI manifest."""
    return _resource_text("manifest.ai")


@mcp.resource("ddg://manifest/status", name="ddg_manifest_status", mime_type="application/json")
def ddg_manifest_status_resource() -> str:
    """DDG public agent status manifest."""
    return _resource_text("manifest.status")


@mcp.resource("ddg://manifest/catalog", name="ddg_manifest_catalog", mime_type="application/json")
def ddg_manifest_catalog_resource() -> str:
    """DDG public service catalog manifest."""
    return _resource_text("manifest.catalog")


@mcp.resource("ddg://manifest/pricing", name="ddg_manifest_pricing", mime_type="application/json")
def ddg_manifest_pricing_resource() -> str:
    """DDG public agent pricing manifest."""
    return _resource_text("manifest.pricing")


@mcp.resource("ddg://manifest/checkout-conformance", name="ddg_manifest_checkout_conformance", mime_type="application/json")
def ddg_manifest_checkout_conformance_resource() -> str:
    """DDG public checkout conformance profile."""
    return _resource_text("manifest.checkout_conformance")


@mcp.resource("ddg://manifest/refund-policy", name="ddg_manifest_refund_policy", mime_type="application/json")
def ddg_manifest_refund_policy_resource() -> str:
    """DDG strict refund/reversal policy for AI-agent paid work."""
    return _resource_text("manifest.refund_policy")


@mcp.resource("ddg://manifest/cybersecurity-services", name="ddg_manifest_cybersecurity_services", mime_type="application/json")
def ddg_manifest_cybersecurity_services_resource() -> str:
    """DDG public cybersecurity service catalog."""
    return _resource_text("manifest.cybersecurity_services")


@mcp.resource("ddg://docs/llms", name="ddg_docs_llms", mime_type="text/plain")
def ddg_docs_llms_resource() -> str:
    """DDG llms.txt for AI-agent discovery."""
    return _resource_text("docs.llms")


@mcp.resource("ddg://docs/mcp-design", name="ddg_docs_mcp_design", mime_type="text/markdown")
def ddg_docs_mcp_design_resource() -> str:
    """DDG MCP design notes for AI-agent clients."""
    return _resource_text("docs.mcp_design")


@mcp.resource("ddg://openapi", name="ddg_openapi", mime_type="application/json")
def ddg_openapi_resource() -> str:
    """DDG OpenAPI contract."""
    return _resource_text("openapi")


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
