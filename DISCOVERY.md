# AI-Agent Discovery Guide

This file is for buyer agents, agent-runtime maintainers, and directory/registry reviewers who need to decide whether DDG Agent-Payable Services are callable, safe, and relevant.

## Canonical service surface

```text
https://agents.daedalusdevelopmentgroup.com
```

## Machine-readable entry points

| Surface | URL | What an agent should use it for |
| --- | --- | --- |
| AI discovery | `https://agents.daedalusdevelopmentgroup.com/.well-known/ai` | First-pass service summary and links |
| Status | `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-status.json` | Live rail/service/MCP readiness |
| API catalog | `https://agents.daedalusdevelopmentgroup.com/.well-known/api-catalog` | Linkset pointing to canonical API assets |
| OpenAPI | `https://agents.daedalusdevelopmentgroup.com/openapi.json` | Request/response schemas and routes |
| llms.txt | `https://agents.daedalusdevelopmentgroup.com/llms.txt` | LLM-readable usage notes |
| Pricing | `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json` | Service pricing and payment metadata |
| Agent catalog | `https://agents.daedalusdevelopmentgroup.com/.well-known/agent-catalog.json` | Agent-buyable service descriptions |
| Agent skills | `https://agents.daedalusdevelopmentgroup.com/.well-known/agent-skills/index.json` | Skill-specific service discovery |
| Checkout conformance | `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-checkout-conformance.json` | 403/402/payment/idempotency contract |
| Refund/reversal policy | `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-refund-policy.json` | Strict no-free-work reversal and entitlement-revocation policy |
| MCP design/status | `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-swarm-mcp-design.md` | MCP wrapper design and current status |

## Current payment rails

Live now:

```text
x402
direct_crypto_auto
direct_crypto_manual
```

Accepted crypto options exposed to buyer agents:

- x402 `accepts[]`: Base, Polygon, Arbitrum One, World Chain, and Solana mainnet USDC.
- Direct crypto public receiving-address families: EVM/stablecoins, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, and XMR.
- Direct crypto proofs are auto-verified only for verifier-supported assets; the remaining public address families are operator-confirmed before fulfillment.

Installed but settlement-proven live yet:

```text
mpp
```

MPP / Stripe / Tempo must remain pending until a real penny-scale settlement succeeds, idempotency replay passes, invalid-token failure stays closed, the public status/pricing/catalog are updated, and all submission packets are re-synced.

## How I expect buyer agents to find DDG

A capable agent looking for services such as `x402 checkout conformance`, `MCP tool security audit`, `agent discovery repair`, or `browser proof artifact` will usually search in this order:

1. General web search / GitHub search for exact task keywords.
2. x402 ecosystem discovery: CDP Bazaar, x402scan, x402 ecosystem page, and x402 awesome lists.
3. MCP ecosystem discovery: official MCP Registry, MCP server aggregators, and GitHub topics.
4. Machine-readable files on service domains: `/.well-known/ai`, `/llms.txt`, `/openapi.json`, `/.well-known/agent-catalog.json`, `/.well-known/agent-skills/index.json`, and status/conformance JSON.
5. Package registries for installable tools: npm, PyPI, OCI/GHCR, or MCPB once a package is released.
6. Social/indexable proof: posts and docs that link directly to machine-readable endpoints instead of vague landing pages.

## Directory/registry readiness

Ready now after security audit:

- public GitHub repo packet
- owned machine-readable discovery surfaces (`/.well-known/ai`, `llms.txt`, OpenAPI, pricing, catalog, agent skills)
- MCP `ddg://distribution/agent-radar`, `ddg://distribution/x402scan-status`, and `ddg://distribution/x402-chains` resources for agent clients
- x402scan registration is live for `agents.daedalusdevelopmentgroup.com` with 5 validated resources; keep AgentCash/x402scan probes green after every OpenAPI/payment-edge/submission change.
- x402 / agent-commerce awesome-list PR copy
- x402 ecosystem listing request copy
- search-indexed docs and social links to machine-readable endpoints

Ready only after additional work:

- CDP x402 Bazaar: requires CDP Facilitator settlement with route discovery metadata and `paymentPayload.resource`.
- Official MCP Registry: requires a public installable package on a supported registry (PyPI for this stdio wrapper) or a public HTTP/Streamable MCP endpoint plus MCP Registry metadata/namespace verification.
- npm/PyPI package listing: requires packaging and release workflow for the stdio MCP wrapper.

## Security posture

DDG sells bounded artifacts/results and proof bundles. DDG does not sell or publish raw provider account access, OAuth tokens, provider API keys, private model IDs, private payment material, raw payment tokens, or verifier sidecar URLs.
