<!-- mcp-name: io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp -->
# DDG Agent-Payable Services

AI-agent-native services from Daedalus Development Group (DDG): checkout/payment conformance, MCP/tool security audits, agent-discovery repair, buyer-agent smoke probes, browser proof, repo context packs, and bounded DDG-operated model/artifact orders.

Production base URL:

```text
https://agents.daedalusdevelopmentgroup.com
```

## Current live payment rails

```text
x402
direct_crypto_auto
direct_crypto_manual
```

Accepted crypto is intentionally broad but bounded by public receiving-address custody and verifier support:

- x402 `accepts[]`: Base, Polygon, Arbitrum One, World Chain, and Solana mainnet USDC.
- Direct crypto public receiving-address families: EVM/stablecoins, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, and XMR.
- Auto verification applies only where the verifier can prove settlement; otherwise `/v1/order-intake` records a hashed proof for operator confirmation before fulfillment.

MPP / Tempo is now advertised in the public 402 challenge with the verifier reporting ready:true and invalid-token failure verified. The remaining proof is one real buyer-funded penny settlement/idempotent replay before calling the MPP money flow fully witnessed. Stripe SPT remains planned.

## Start here if you are a buyer agent

1. Fetch AI discovery:

```bash
tmp=$(mktemp)
curl -fsS -o "$tmp" https://agents.daedalusdevelopmentgroup.com/.well-known/ai
python3 -m json.tool "$tmp"
```

2. Fetch status:

```bash
tmp=$(mktemp)
curl -fsS -o "$tmp" https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-status.json
python3 -m json.tool "$tmp"
```

3. Fetch pricing/catalog:

```bash
tmp_pricing=$(mktemp)
tmp_catalog=$(mktemp)
curl -fsS -o "$tmp_pricing" https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json
curl -fsS -o "$tmp_catalog" https://agents.daedalusdevelopmentgroup.com/.well-known/agent-catalog.json
python3 -m json.tool "$tmp_pricing"
python3 -m json.tool "$tmp_catalog"
```

4. Verify checkout conformance:

```bash
tmp=$(mktemp)
curl -fsS -o "$tmp" https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-checkout-conformance.json
python3 -m json.tool "$tmp"
```

5. Probe the payment gate without spending:

```bash
curl -i -X POST https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test \
  -H 'Content-Type: application/json' \
  -H 'X-Agent-Id: your-agent-id' \
  -d '{"service":"tx_penny_smoke_test"}'
```

Expected without payment: `402 payment_required` with accepted protocols.

## Important endpoints

See also [`DISCOVERY.md`](DISCOVERY.md) for the agent-radar/distribution map and directory readiness notes.

| Endpoint | Purpose |
| --- | --- |
| `/.well-known/ai` | AI-agent discovery surface |
| `/.well-known/ddg-agent-status.json` | Rail/service/MCP status |
| `/.well-known/api-catalog` | Linkset API catalog |
| `/openapi.json` | OpenAPI contract |
| `/llms.txt` | LLM-facing instructions |
| `/.well-known/ddg-agent-pricing.json` | Machine-readable pricing |
| `/.well-known/agent-catalog.json` | Agent service catalog |
| `/.well-known/agent-skills/index.json` | Agent-skill discovery index |
| `/.well-known/ddg-agent-checkout-conformance.json` | Checkout conformance profile |
| `/.well-known/ddg-agent-refund-policy.json` | Strict refund/reversal policy for agent-paid work |
| `/.well-known/ddg-agent-swarm-mcp-design.md` | MCP design/status doc |

## Flagship services

- `agent_payment_readiness_audit`
- `mcp_tool_security_audit`
- `agent_service_distribution_pack`
- `agent_marketplace_listing_pack`
- `agent_readiness_scorecard`
- `buyer_agent_smoke_probe`
- `browser_proof`
- `repo_context_pack`
- `ai_skill_safety_scan`
- `model_agent_run`

## MCP

The local stdio MCP server is in [`mcp/`](mcp/). It exposes free discovery/status/conformance tools, allowlisted `ddg://` resources for public manifests/docs/OpenAPI, agent-radar/x402 Bazaar readiness metadata, and payment-aware paid-service helpers. Paid tools return structured `402 payment_required` challenges instead of opaque MCP errors.

Current MCP status: stdio package/source is locally smoke-tested and the hosted Streamable HTTP endpoint is live at `https://mcp.daedalusdevelopmentgroup.com/mcp` with public MCP-client smoke passing. See [`docs/mcp-production-readiness.md`](docs/mcp-production-readiness.md).

## Security and compliance stance

DDG sells bounded artifacts/results, not raw model-provider account access. DDG never sells, returns, or relays:

- raw OAuth tokens
- provider API keys
- private account/session state
- raw provider seats
- private model IDs when they would reveal account mechanics
- raw payment tokens or verifier sidecar URLs

Provider-backed model capacity is packaged as DDG-operated artifact/result delivery with spend caps, output schemas, redaction, receipts, and operator review where needed.

## Repository contents

```text
openapi.json                         Public OpenAPI contract copy
docs/pricing.json                    Pricing copy
docs/agent-catalog.json              Catalog copy
docs/agent-status.json               Status copy
docs/checkout-conformance.json       Checkout profile copy
docs/agent-skills/                   Agent skill JSON files
mcp/                                 Local stdio MCP server and metadata
scripts/agent_checkout_conformance_probe.py  Probe script
examples/                            Curl and Python buyer-agent examples
schemas/                             Public JSON schema drafts
```

## Contact

Operator contact: `0xcircuitbreaker@protonmail.com`
