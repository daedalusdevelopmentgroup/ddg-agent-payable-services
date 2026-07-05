# x402scan registration packet — DDG Agent-Payable Services

Use this packet for `https://www.x402scan.com/resources/register` or equivalent x402 directory review.

Last sync: `2026-06-24T01:32:05Z`

## x402scan live registration status

Registered successfully on x402scan using:

```text
agents.daedalusdevelopmentgroup.com
```

Public pages:

- x402scan server page: `https://www.x402scan.com/server/c3540307-0eb2-455d-90b6-a21f7d5a3792`
- Merchant/share page: `https://tryponcho.com/m/agents.daedalusdevelopmentgroup.com`

## x402scan / agentcash preflight status

Current live preflight:

- `npx -y @agentcash/discovery@latest discover https://agents.daedalusdevelopmentgroup.com` exits 0 and reads the live OpenAPI.
- `npx -y @agentcash/discovery@latest check https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test` exits 0 and classifies the one-cent route as paid.
- Direct x402scan `developer.batchTest` reports 5 successful resources and 0 failed resources.
- Runtime `402` bodies include canonical x402 v2 payment requirements plus `extensions.bazaar.schema.properties.input/output` metadata for agent invocation.
- Directory probes return canonical x402 `402` metadata without executing backend work; real work-attempt POSTs without stable AI-agent identity still fail as `403 agent_only`.

Validated resources:

```text
/v1/site-audit
/v1/model/chat-completions
/v1/model/agent-run
/v1/order-intake
/v1/tx-smoke-test
```

Current gate: **keep x402scan/agentcash probes green after every OpenAPI/payment-edge/docs/submission change; CDP Bazaar remains separately settlement-gated.**

## Payment/crypto options to keep synchronized

Live public rails:

```text
x402
direct_crypto_auto
direct_crypto_manual
```

x402 `accepts[]` currently advertises USDC on:

```text
Base mainnet (eip155:8453)
Polygon mainnet (eip155:137)
Arbitrum One (eip155:42161)
World Chain mainnet (eip155:480)
Solana mainnet (solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp)
```

Direct-crypto public receiving-address families:

```text
EVM/stablecoins
BTC
BCH
LTC
DOGE
SOL
TRX
XRP
XLM
ALGO
DOT
ZEC
XMR
```

Automatic direct-crypto verification is limited to verifier-supported assets. The remaining public receiving-address families are operator-confirmed before fulfillment via hashed proof metadata. ADA/Cardano is **not** advertised until a DDG-controlled receiving address and verification/manual-confirmation policy exist.

Pending and settlement-proven live:

```text
mpp
```

## Submission sync rule

Before any other listing/submission/PR, update all of these together and run `python3 scripts/validate_submission_sync.py`:

- `openapi.json`
- `docs/pricing.json`
- `docs/agent-catalog.json`
- `docs/agent-status.json`
- `docs/ai-discovery.json`, `docs/agents.json`, `docs/llms.txt`, `docs/quickstart.md`
- `submissions/x402scan/ddg-agent-services-registration.md`
- `submissions/x402-ecosystem/awesome-x402-listing.md`
- `submissions/x402-bazaar/settlement-metadata.json`
- `submissions/mcp-registry/ddg-agent-services-publish.md`
- `README.md`, `DISCOVERY.md`, and MCP distribution resources/tools

## Spec requirements

- OpenAPI at `/openapi.json` is the canonical discovery contract.
- Paid operations need `responses.402`, `x-payment-info.price`, `x-payment-info.protocols`, and a runnable request schema/example so probes can reach the paywall.
- Runtime `402` challenge behavior is the final source of truth.
- Free/non-x402 endpoints should be marked with `security: []` or otherwise not advertised as paid resources.
- MPP/Tempo is settlement-proven for tx-smoke. Keep x402/CDP facilitator settlement and indexing pending until CDP business approval/credentials or a self-hosted facilitator path proves settlement, idempotency replay, fake-token 402, and leak scan.

Local preflight after any deploy:

```bash
npx -y @agentcash/discovery@latest discover https://agents.daedalusdevelopmentgroup.com
npx -y @agentcash/discovery@latest check https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test
python3 scripts/validate_submission_sync.py
```

## Primary registered smoke resource

```text
https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test
```

Why this first: it is side-effect-free except payment verification/receipt handling and costs one cent, so buyer agents and directory scanners can safely test DDG's payment ladder.

## API details

- Method: `POST`
- OpenAPI: `https://agents.daedalusdevelopmentgroup.com/openapi.json`
- Discovery: `https://agents.daedalusdevelopmentgroup.com/.well-known/ai`
- llms.txt: `https://agents.daedalusdevelopmentgroup.com/llms.txt`
- Pricing: `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json`
- Direct-crypto public manifest: `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-direct-crypto-addresses.json`
- Checkout conformance: `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-checkout-conformance.json`
- Strict refund/reversal policy: `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-refund-policy.json`
- GitHub: `https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services`

## Listing copy

```text
DDG Agent Services is a pay-per-call AI agent services gateway: one x402/direct-crypto entry point for callable tools, OpenAI-compatible routes, payment readiness, MCP security checks, discovery repair, receipts, browser proof artifacts, and repo context packs. The one-cent tx-smoke-test endpoint lets buyer agents verify x402 and direct-crypto payment handling without triggering expensive compute.
```

## Recommended x402scan title/description

```text
Title: DDG Agent Services - pay-per-call AI agent services gateway
Description: One x402/direct-crypto entry point for AI-agent callable tools, OpenAI-compatible routes, payment readiness, MCP security checks, discovery repair, receipts, browser proof artifacts, and repo context packs. Start with a one-cent payment smoke test.
```

## Keywords

```text
x402, AI agents, agent commerce, MCP security, checkout conformance, payment readiness audit, buyer-agent smoke probe, direct crypto, OpenAPI, llms.txt
```

## Contact

```text
0xcircuitbreaker@protonmail.com
```

## Expected unauthenticated/unpaid behavior

Without an agent identity header, protected routes should return `403 agent_only`.

With an agent identity but no valid payment, `/v1/tx-smoke-test` should return `402 payment_required` with accepted protocols containing only currently live rails.

A fake/mock payment in production should remain rejected with `402 payment_required`.

## CDP Bazaar caveat

This x402scan packet is ready for directory review, but CDP x402 Bazaar indexing is separate. Bazaar requires a successful CDP Facilitator settle call with Bazaar discovery metadata and `paymentPayload.resource` set. Do not claim Bazaar indexing until discovery search or the Bazaar MCP endpoint returns the DDG resource.
