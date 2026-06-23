# x402scan registration packet — DDG Agent-Payable Services

Use this packet for `https://www.x402scan.com/resources/register` or equivalent x402 directory review.

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

- `npx -y @agentcash/discovery@latest discover https://agents.daedalusdevelopmentgroup.com` exits 0 and reads 19 routes from the live OpenAPI.
- `npx -y @agentcash/discovery@latest check https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test` exits 0 and classifies the one-cent route as paid.
- Direct x402scan `developer.batchTest` reports 5 successful resources and 0 failed resources.
- Runtime `402` bodies now include canonical x402 v2 payment requirements plus `extensions.bazaar.schema.properties.input/output` metadata for agent invocation.
- The only remaining AgentCash discovery warning is cosmetic `FAVICON_MISSING`.

Validated resources:

```text
/v1/site-audit
/v1/model/chat-completions
/v1/model/agent-run
/v1/order-intake
/v1/tx-smoke-test
```

Current gate: **keep x402scan/agentcash probes green after every OpenAPI/payment-edge change; CDP Bazaar remains separately settlement-gated.**

Spec requirements:

- OpenAPI at `/openapi.json` is the canonical discovery contract.
- Paid operations need `responses.402`, `x-payment-info.price`, `x-payment-info.protocols`, and a runnable request schema/example so probes can reach the paywall.
- Runtime `402` challenge behavior is the final source of truth.
- Free/non-x402 endpoints should be marked with `security: []` or otherwise not advertised as paid resources.

Local preflight after deploy:

```bash
npx -y @agentcash/discovery@latest discover https://agents.daedalusdevelopmentgroup.com
npx -y @agentcash/discovery@latest check https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test
```

## Resource to register after the blocker is fixed

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
- Checkout conformance: `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-checkout-conformance.json`
- Strict refund/reversal policy: `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-refund-policy.json`
- GitHub: `https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services`

## Listing copy

```text
DDG Agent-Payable Services provides AI-agent-native checkout/payment conformance, MCP/tool security audits, agent-discovery repair, buyer-agent smoke probes, browser proof artifacts, and repo context packs. The one-cent tx-smoke-test endpoint lets buyer agents verify x402/direct-crypto payment handling without triggering expensive compute.
```

## Keywords

```text
x402, AI agents, agent commerce, MCP security, checkout conformance, payment readiness audit, buyer-agent smoke probe, OpenAPI, llms.txt
```

## Contact

```text
0xcircuitbreaker@protonmail.com
```

## Current payment rails

Live public rails:

```text
x402
direct_crypto_auto
```

Pending and not advertised live:

```text
mpp
```

## Expected unauthenticated/unpaid behavior

Without an agent identity header, protected routes should return `403 agent_only`.

With an agent identity but no valid payment, `/v1/tx-smoke-test` should return `402 payment_required` with accepted protocols containing only currently live rails.

A fake/mock payment in production should remain rejected with `402 payment_required`.

## CDP Bazaar caveat

This x402scan packet is ready for directory review, but CDP x402 Bazaar indexing is separate. Bazaar requires a successful CDP Facilitator settle call with Bazaar discovery metadata and `paymentPayload.resource` set. Do not claim Bazaar indexing until discovery search or the Bazaar MCP endpoint returns the DDG resource.
