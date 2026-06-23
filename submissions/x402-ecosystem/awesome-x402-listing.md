# DDG x402 ecosystem / awesome-x402 listing packet

Use this copy for x402 ecosystem pages, awesome-list PRs, or directory submissions after the public payment-ladder smoke remains green.

## Listing title

DDG Agent-Payable Services

## URL

https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services

## Primary payable resource

https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test

## Description

DDG Agent-Payable Services provides AI-agent-native checkout/payment conformance, MCP/tool security audits, agent-discovery repair, buyer-agent smoke probes, browser proof artifacts, and repo context packs. The one-cent tx-smoke-test endpoint lets buyer agents verify x402/direct-crypto payment handling without triggering expensive compute.

## Discovery links

- AI manifest: https://agents.daedalusdevelopmentgroup.com/.well-known/ai
- OpenAPI: https://agents.daedalusdevelopmentgroup.com/openapi.json
- llms.txt: https://agents.daedalusdevelopmentgroup.com/llms.txt
- Pricing: https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json
- Checkout conformance: https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-checkout-conformance.json
- Strict refund/reversal policy: https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-refund-policy.json
- Agent catalog: https://agents.daedalusdevelopmentgroup.com/.well-known/agent-catalog.json

## Payment rails to claim publicly

Live now:

- x402 (Base mainnet USDC; accepts[] also advertises Polygon, Arbitrum, World Chain, Solana)
- direct_crypto_auto (13 asset families: EVM, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, ADA, DOT, XLM, ALGO, ZEC, XMR)

Pending / do not claim live yet:

- MPP / Stripe machine-payments, until provider env, health, settlement, idempotency, and fake-token failure checks pass.
- CDP x402 Bazaar indexing, until a real CDP Facilitator settle call with Bazaar metadata and `paymentPayload.resource` completes and Bazaar search/MCP returns DDG.

## Pre-submit checks

```bash
# From the DDG payment-edge operations workspace, verify the public payment ladder first:
# run the maintained ddg_public_https_smoke.sh against https://agents.daedalusdevelopmentgroup.com

# Then re-run the x402scan registration form against:
# https://www.x402scan.com/resources/register
# domain: agents.daedalusdevelopmentgroup.com
```

Only submit if the smoke check passes and the x402 directory probe reports valid paid resources rather than `0 valid resources` / `[501] Endpoint did not return a 402 payment challenge`.
