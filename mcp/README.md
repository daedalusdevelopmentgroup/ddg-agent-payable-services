# DDG Agent-Payable Services MCP

Local stdio MCP wrapper for `https://agents.daedalusdevelopmentgroup.com`. It exposes DDG discovery, status, conformance, order-polling, free safety scan, and payment-aware paid-service helpers to MCP-capable agents.

## Status

- **stdio package/skeleton:** package-ready and locally smoke-tested.
- **HTTP/Streamable MCP:** local streamable-http support added; public production endpoint is planned and must be deployed/smoked before registry remote listing.
- **PyPI package metadata:** staged as `ddg-agent-services-mcp` with MCP Registry name `io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp`.
- **Public service base:** `https://agents.daedalusdevelopmentgroup.com`
- **Public design doc:** `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-swarm-mcp-design.md`

DDG never returns provider credentials, private CLI auth state, account seats, raw provider sessions, private model IDs, or raw payment material.

## Install/run locally

```bash
cd /path/to/hermes
DDG_MCP_AGENT_ID="your-agent-or-swarm-id" \
DDG_AGENT_SERVICES_BASE_URL="https://agents.daedalusdevelopmentgroup.com" \
uv run --with mcp python sales_artifacts/agent_payments/mcp/ddg_agent_services_mcp_server.py
```

## Hermes native MCP config

Add this to `~/.hermes/config.yaml`, then restart Hermes:

```yaml
mcp_servers:
  ddg_agent_services:
    command: "uv"
    args:
      - "run"
      - "--with"
      - "mcp"
      - "python"
      - "/absolute/path/to/hermes/sales_artifacts/agent_payments/mcp/ddg_agent_services_mcp_server.py"
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
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp",
        "python",
        "/absolute/path/to/hermes/sales_artifacts/agent_payments/mcp/ddg_agent_services_mcp_server.py"
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

## Payment flow

Paid tools return the edge's structured `402 payment_required` challenge instead of opaque MCP errors. A buyer agent can inspect accepted rails, pay through x402/direct-crypto/MPP when live, and retry with payment headers.

Current public live rails:

```text
x402
direct_crypto_auto
```

MPP is installed but not advertised live until `/health.ready=true`, a public 402 challenge includes MPP, a real penny-scale MPP settlement succeeds, idempotency replay passes, and invalid-token failure is verified.

## Local smoke result

Smoke command used:

```bash
uv run --with mcp python /tmp/ddg_mcp_stdio_smoke.py
```

Observed result:

```json
{
  "agent_status_status": 200,
  "conformance_status": 200,
  "receipt_design_status": "planned_not_live",
  "skill_scan_status": 200,
  "tx_smoke_status": 402,
  "tx_smoke_error": "payment_required",
  "tx_accepted_protocols": ["x402", "direct_crypto_auto"]
}
```

## Security boundaries

- No arbitrary shell, eval, or file-write tools.
- No raw provider/session/OAuth/account credential relay.
- No raw upstream provider rate-limit headers or private model IDs in output.
- Tool outputs are bounded; large artifacts return URLs/hashes.
- Dynamic scanning and browser/code execution stay sandboxed/operator-reviewed service artifacts.
- The stdio wrapper only forwards a small allowlist of payment/idempotency headers.
