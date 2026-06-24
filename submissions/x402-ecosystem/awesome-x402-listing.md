# DDG x402 ecosystem / awesome-x402 listing packet

Use this copy for x402 ecosystem pages, awesome-list PRs, or directory submissions after the public payment-ladder smoke remains green.

Last sync: `2026-06-24T01:32:05Z`

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
- Direct-crypto public manifest: https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-direct-crypto-addresses.json
- Checkout conformance: https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-checkout-conformance.json
- Strict refund/reversal policy: https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-refund-policy.json
- Agent catalog: https://agents.daedalusdevelopmentgroup.com/.well-known/agent-catalog.json
- x402scan server page: https://www.x402scan.com/server/c3540307-0eb2-455d-90b6-a21f7d5a3792

## Payment rails to claim publicly

Live now:

- x402 (Base mainnet USDC first for x402scan/CDP compatibility; `accepts[]` also advertises Polygon, Arbitrum One, World Chain, and Solana mainnet USDC)
- direct_crypto_auto (only verifier-supported assets are auto-confirmed)
- direct_crypto_manual (operator-confirmed fallback using public receiving-address families)

Direct-crypto public receiving-address families:

```text
EVM/stablecoins, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, XMR
```

ADA/Cardano is not advertised until a DDG-controlled receiving address and verification/manual-confirmation policy exist.

Pending / do not claim live yet:

- MPP / Stripe machine-payments, until provider env, health, settlement, idempotency, and fake-token failure checks pass.
- CDP x402 Bazaar indexing, until a real CDP Facilitator settle call with Bazaar metadata and `paymentPayload.resource` completes and Bazaar search/MCP returns DDG.

## awesome-x402 entry format

```markdown
- [DDG Agent-Payable Services](https://agents.daedalusdevelopmentgroup.com) - AI-agent-native x402/direct-crypto services for checkout conformance, MCP/tool security audits, agent-discovery repair, buyer-agent smoke probes, browser proof artifacts, and repo context packs.
```

## Pre-submit checks

```bash
# From the public repo packet:
python3 scripts/validate_submission_sync.py
PYTHONDONTWRITEBYTECODE=1 uv run --extra dev pytest

# From the DDG payment-edge operations workspace, verify the public payment ladder first:
# run the maintained ddg_public_https_smoke.sh against https://agents.daedalusdevelopmentgroup.com

# Then re-run:
npx -y @agentcash/discovery@latest discover https://agents.daedalusdevelopmentgroup.com
npx -y @agentcash/discovery@latest check https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test
```

Only submit if the smoke check passes and the x402 directory probe reports valid paid resources with no scanner-compatibility regression.
