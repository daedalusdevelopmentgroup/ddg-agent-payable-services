# DDG Agent Services MCP Server Design

Status: **source/stdio skeleton expanded; production HTTP/Streamable MCP deployment pending**.
Audience: AI-agent swarms that want to discover, quote, pay for, and use DDG agent-payable services without manually reading every OpenAPI/pricing document.

## Public positioning

DDG will expose an agent-native MCP server that wraps `https://agents.daedalusdevelopmentgroup.com` with safe, payment-aware tools. The MCP server does **not** expose provider API keys, OAuth/account sessions, raw credentials, private payment material, raw LAN backends, or private provider model IDs. It returns machine-readable payment challenges/receipts and routes paid work through the DDG payment edge.

The MCP server's value is not generic model proxying. Its value is **proof + repair + security + status/artifact retrieval** for buyer agents.

## Initial transports

1. **stdio package for local agents** — quickest adoption path for Claude Desktop, Codex/OpenCode-style swarms, Hermes, VS Code, and Zed.
2. **HTTP/StreamableHTTP endpoint** — hosted MCP endpoint behind Cloudflare after identity, rate limits, request-size limits, and payment challenge handling are verified.

Target package/registry identity:

- npm package: `@daedalusdevelopmentgroup/ddg-agent-services-mcp`
- MCP title: `DDG Agent-Payable Services MCP`
- homepage: `https://agents.daedalusdevelopmentgroup.com/.well-known/ai`

## P0 tools — free/discovery/status

These should ship first because they make DDG discoverable and safe to evaluate without spending.

| Tool | Payment | Purpose |
| --- | --- | --- |
| `ddg_list_services` | Free | Fetch pricing/catalog and summarize live vs manual vs planned services. |
| `ddg_agent_status` | Free | Fetch `/.well-known/ddg-agent-status.json`: live rails, MPP state, discovery links, service counts. |
| `ddg_checkout_conformance` | Free | Fetch the public checkout conformance profile. |
| `ddg_list_models` | Free | Fetch `/v1/ollama-models` and public queryable route labels without exposing raw backend URLs. |
| `ddg_list_local_runtime_options` | Free | Surface local runtime options, healthy seat count, lease/request caps, and model request policy. |
| `ddg_skill_safety_scan` | Free lead magnet | Static-only no-execution scan for a supplied skill/workflow markdown. |
| `ddg_security_service_catalog` | Free | Return the DDG AI-agent cybersecurity services catalog. |
| `ddg_order_status` | Free, agent-scoped | Poll an existing order by ID using configured `X-Agent-Id`. |
| `ddg_order_artifact` | Free, agent-scoped | Retrieve a ready/pending order artifact by ID. |
| `ddg_receipt_verify_design` | Planned/free | Placeholder design for future `/v1/receipt-verify` so receipts become portable. |

## P1 tools — payment-aware actions

| Tool | Payment | Behavior |
| --- | --- | --- |
| `ddg_tx_smoke_test` | $0.01 | Exercises `/v1/tx-smoke-test`; returns 402 challenge if unpaid. |
| `ddg_quote_payment` | Free/402 dry-run | Calls a protected route without payment to return accepted rails and price hints. |
| `ddg_submit_order` | Service price | Submits `/v1/order-intake` after the client supplies payment headers/proof. |
| `ddg_run_paid_model` | Metered/route price | Calls `/v1/model/chat-completions` or `/v1/model/agent-run` after valid payment. |
| `ddg_request_ollama_model` | Free/manual queue | Requests a local model/runtime import; never auto-downloads by public request. |

## Payment flow inside MCP

Paid tools must not throw opaque errors when unpaid. They should return structured payment-required results mirroring the public `402` challenge:

```json
{
  "status": 402,
  "body": {
    "error": "payment_required",
    "accepted_protocols": ["x402", "direct_crypto_auto"],
    "x402": { "resource": "https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test" },
    "direct_crypto": { "status": "auto_verification_available" }
  }
}
```

Future MPP support becomes public only after the payment edge advertises MPP in real `402` challenges and a penny-scale settlement/idempotency proof passes.

## Security boundaries

- No arbitrary shell, `eval`, or raw command-execution tools.
- No filesystem write tools.
- No provider/OAuth/session/account credential relay.
- No buyer-supplied secret echoing in results.
- No raw upstream provider rate-limit headers or private model IDs in tool output.
- Tool outputs are bounded; large artifacts should be returned as status/artifact URLs with hashes.
- Browser proof, dynamic MCP fuzzing, repo scanning, package install checks, and code execution remain sandboxed/operator-reviewed service artifacts — not direct MCP tools with arbitrary execution authority.
- HTTP MCP must sit behind Cloudflare plus app-layer `X-Agent-Id`, size/time limits, rate limits, and the DDG payment gate.

## Output/receipt schema direction

Every paid/action tool should eventually return a normalized receipt envelope:

```json
{
  "receipt": {
    "order_id": "string",
    "service_id": "string",
    "amount_usd": 0.01,
    "payment_rail": "x402|direct_crypto|mpp",
    "receipt_hash": "sha256",
    "artifact_hash": "sha256|null",
    "status_url": "https://agents.daedalusdevelopmentgroup.com/v1/orders/...",
    "artifact_url": "https://agents.daedalusdevelopmentgroup.com/v1/orders/.../artifact"
  }
}
```

Do not return buyer contact info, raw payment tokens/proofs, private provider diagnostics, or raw txids unless the buyer explicitly submitted them and the response redacts/hashes them.

## Build phases

1. **P0 stdio skeleton** — expand `ddg_agent_services_mcp_server.py` with discovery/status/conformance/skill-safety/order polling tools. *(In progress.)*
2. **Local stdio smoke** — install `mcp` SDK, run server locally, call P0 tools from Hermes/Claude Desktop, verify no credentials are needed.
3. **Payment dry-run** — call paid tools without credentials; confirm structured 402 challenge is tool-friendly.
4. **Receipt verification endpoint** — implement `/v1/receipt-verify` backed by payment-edge audit/state, then replace the design placeholder tool with a live verifier.
5. **HTTP/Streamable MCP service** — expose under `https://mcp.daedalusdevelopmentgroup.com/mcp` after WAF/rate-limit/auth tests.
6. **Registry package** — publish npm package and registry metadata; submit to official MCP Registry and Awesome MCP lists.
7. **Dynamic security tools** — add paid MCP/security fuzzing only as bounded artifact workflows, not direct arbitrary execution.

## Registry readiness checklist

- [ ] Public README with install snippets for Hermes, Claude Desktop, VS Code/Zed.
- [ ] Versioned tool list and schemas.
- [ ] Security policy.
- [ ] `/.well-known/ai`, `llms.txt`, OpenAPI, pricing, status, conformance links.
- [ ] Demo transcript proving free tool calls and unpaid paid-tool 402 challenge.
- [ ] Clear statement: DDG sells artifacts/results and never raw provider account/session access.
