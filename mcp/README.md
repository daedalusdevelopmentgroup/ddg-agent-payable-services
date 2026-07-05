# DDG Agent-Payable Services MCP

Local stdio MCP wrapper for `https://agents.daedalusdevelopmentgroup.com`. It exposes DDG discovery, status, conformance, order-polling, free safety scan, and payment-aware paid-service helpers to MCP-capable agents.

## Status

- **stdio package/skeleton:** package-ready and locally smoke-tested.
- **HTTP/Streamable MCP:** public production endpoint is live at `https://mcp.daedalusdevelopmentgroup.com/mcp` and MCP-client smoked; plain browser/curl requests without `Accept: text/event-stream` receive the normal Streamable HTTP negotiation `406`.
- **PyPI package:** published as `ddg-agent-services-mcp` with MCP Registry name `io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp`.
- **Official MCP Registry:** `server.json` validates; final publication is blocked only on the `mcp-publisher` auth/publish flow.
- **Production checklist:** [`../docs/mcp-production-readiness.md`](../docs/mcp-production-readiness.md).
- **Public service base:** `https://agents.daedalusdevelopmentgroup.com`
- **Public design doc:** `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-swarm-mcp-design.md`

DDG never returns provider credentials, private CLI auth state, account seats, raw provider sessions, private model IDs, or raw payment material.

## Install/run locally

```bash
cd /path/to/ddg-agent-payable-services
DDG_MCP_AGENT_ID="your-agent-or-swarm-id" \
DDG_AGENT_SERVICES_BASE_URL="https://agents.daedalusdevelopmentgroup.com" \
uv run --extra dev python -m ddg_agent_services_mcp
```

## Hermes native MCP config

Add this to `~/.hermes/config.yaml`, then restart Hermes:

```yaml
mcp_servers:
  ddg_agent_services:
    command: "uvx"
    args:
      - "ddg-agent-services-mcp"
    env:
      DDG_MCP_AGENT_ID: "your-agent-or-swarm-id"
      DDG_AGENT_SERVICES_BASE_URL: "https://agents.daedalusdevelopmentgroup.com"
    timeout: 120
    connect_timeout: 60
```

Hermes registers tool names like:

```text
mcp_ddg_agent_services_ddg_list_services
mcp_ddg_agent_services_ddg_agent_status
```

## Claude Desktop / generic MCP config

```json
{
  "mcpServers": {
    "ddg-agent-services": {
      "command": "uvx",
      "args": [
        "ddg-agent-services-mcp"
      ],
      "env": {
        "DDG_MCP_AGENT_ID": "your-agent-or-swarm-id",
        "DDG_AGENT_SERVICES_BASE_URL": "https://agents.daedalusdevelopmentgroup.com"
      }
    }
  }
}
```

## P0 tools

| Tool | Payment | Purpose |
| --- | --- | --- |
| `ddg_mcp_security_profile` | Free | Report local wrapper controls, publication gates, and header/payload/resource safety limits. |
| `ddg_public_resource_index` | Free | List allowlisted `ddg://` manifest/doc resources. |
| `ddg_fetch_public_resource` | Free | Fetch an allowlisted public resource by id or URI with size caps and redaction. |
| `ddg_agent_distribution_targets` | Free | Show AI-agent radar targets: owned discovery, GitHub, MCP Registry, CDP x402 Bazaar, x402scan, ecosystem lists, and MCP aggregators. |
| `ddg_x402_bazaar_readiness` | Free | Return CDP x402 Bazaar candidate resources, JSON Schemas, and settlement/indexing gates. |
| `ddg_list_services` | Free | Fetch pricing/catalog. |
| `ddg_agent_status` | Free | Fetch `/.well-known/ddg-agent-status.json`. |
| `ddg_checkout_conformance` | Free | Fetch checkout conformance profile. |
| `ddg_list_models` | Free | Fetch public local/model route labels. |
| `ddg_list_local_runtime_options` | Free | Inspect local runtime options and free-seat policy. |
| `ddg_skill_safety_scan` | Free | Static-only no-execution scan of supplied skill/workflow text. |
| `ddg_security_service_catalog` | Free | Return cybersecurity services catalog. |
| `ddg_order_status` | Free, agent-scoped | Poll order status by ID. |
| `ddg_order_artifact` | Free, agent-scoped | Fetch order artifact by ID. |
| `ddg_receipt_verify_design` | Planned/free | Describes future receipt verification endpoint. |

## Payment-aware tools

| Tool | Payment | Behavior |
| --- | --- | --- |
| `ddg_tx_smoke_test` | $0.01 | Returns structured 402 if unpaid; verifies buyer payment stack when paid. |
| `ddg_quote_payment` | Free/402 dry-run | Intentionally triggers a payment challenge for a protected route. |
| `ddg_submit_order` | Service price | Submits `/v1/order-intake` after caller supplies payment proof. |
| `ddg_run_paid_model` | Metered/route price | Calls model/chat or agent-run routes after valid payment. |
| `ddg_request_ollama_model` | Free/manual queue | Requests a local model/runtime import; never auto-downloads by public request. |

## MCP resources

The server also exposes allowlisted public resources for agent discovery clients:

```text
ddg://manifest/ai
ddg://manifest/status
ddg://manifest/catalog
ddg://manifest/pricing
ddg://manifest/checkout-conformance
ddg://manifest/cybersecurity-services
ddg://docs/llms
ddg://docs/mcp-design
ddg://openapi
ddg://distribution/agent-radar
ddg://distribution/x402-bazaar-readiness
```

Resources are fetched only from fixed DDG public paths or returned from static source-bundled distribution metadata, never from arbitrary URLs. Responses are size-capped and secret-pattern redacted before returning to the MCP client.

## Payment flow

Paid tools return the edge's structured `402 payment_required` challenge instead of opaque MCP errors. A buyer agent can inspect accepted rails, pay through x402/direct-crypto/MPP when live, and retry with payment headers. Hosted/remote MCP clients should pass a stable `agent_id` tool argument on paid and order-scoped tools so payment/order scope stays buyer-specific instead of collapsing into the server default identity.

Current public live rails:

```text
x402
direct_crypto_auto
```

MPP is installed but settlement-proven live until `/health.ready=true`, a public 402 challenge includes MPP, a real penny-scale MPP settlement succeeds, idempotency replay passes, and invalid-token failure is verified.

## Local smoke result

Smoke commands used:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
DDG_MCP_AGENT_ID=ddg-mcp-stdio-smoke \
uv run --extra dev python scripts/smoke_mcp_server.py --transport stdio

PYTHONDONTWRITEBYTECODE=1 \
uv run --extra dev python scripts/smoke_mcp_server.py \
  --transport streamable-http \
  --http-url http://127.0.0.1:8891/mcp \
  --agent-id ddg-mcp-http-smoke
```

Observed result shape:

```json
{
  "ok": true,
  "tool_count": 20,
  "resource_count": 11,
  "sample": {
    "security_profile_status": "source_hardened_public_remote_live",
    "agent_status_status": 200,
    "checkout_conformance_status": 200,
    "receipt_design_status": "planned_not_live",
    "tx_smoke_status": 402,
    "tx_smoke_error": "payment_required",
    "tx_accepted_protocols": ["MPP", "x402", "direct_crypto_auto", "direct_crypto_manual"]
  }
}
```

## Security boundaries

- No arbitrary shell, eval, or file-write tools.
- No raw provider/session/OAuth/account credential relay.
- No raw upstream provider rate-limit headers or private model IDs in output.
- Tool outputs and MCP resource reads are bounded; large artifacts return URLs/hashes.
- Upstream JSON/string bodies are redacted for secret-like keys and values before return.
- Dynamic scanning and browser/code execution stay sandboxed/operator-reviewed service artifacts.
- The wrapper only forwards a small allowlist of payment/idempotency headers; generic Bearer/Basic credentials are dropped.
