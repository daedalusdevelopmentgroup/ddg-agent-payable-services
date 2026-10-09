<!-- mcp-name: com.daedalusdevelopmentgroup/ddg-agent-services-mcp -->
mcp-name: com.daedalusdevelopmentgroup/ddg-agent-services-mcp
# DDG Agent-Payable Revenue Launch Pack

This directory contains the machine-readable launch artifacts and local scaffold for turning Hermes/DDG into a paid service surface for other AI agents.

## Current launch wedges

1. **One-cent transaction smoke test** (`/v1/tx-smoke-test`) — $0.01 receipt-only paid request so other AI agents can prove they can complete a DDG paid HTTP transaction.
2. **Website audit** (`/v1/site-audit`) — read-only; launch settlement-test price $0.75.
3. **Model router / basic conversation** (`/v1/model/chat-completions`, `/v1/model/agent-run`) — paid access to DDG-operated model routing using explicit model aliases; supports basic chat, analysis, code/help prompts, and bounded agent tasks.
4. **Operator-reviewed OAuth/model artifact run** (`service_id=provider_model_artifact_order` through `/v1/order-intake`) — DDG-operated account/provider-backed model work only where terms permit; no raw token/account/seat resale.
5. **Lead pack** (`/v1/lead-pack`) — paid local business intelligence; launch price $5.
6. **Browser proof** (`/v1/browser-proof`) — paid screenshots/QA proof; launch price $2.
7. **Outreach brief** (`/v1/outreach-brief`) — paid draft only; no sending without human approval; launch price $1.50.
8. **Ethereum private RPC query** (`/v1/ethereum/rpc`) — implemented read-only, method-whitelisted Reth proxy with sync gate, fair-use lease timer, per-agent request caps, max batch size, and upstream max-concurrency cap; public self-serve waits for execution sync/health.
9. **Local model free-seat pool** (`/v1/micro-model-swarm-preview`, `/v1/model/agent-run`, `/v1/ollama-models`) — live free/best-effort Ollama local routes with one concurrent generation seat per healthy configured local runtime backend, capped at two by default for configured 8GB-VRAM backends. Defaults: 24-hour per-agent lease, 100 requests/lease, 60s swarm generation timeout, 120s local agent-run timeout. The named paid lease path remains planned.
10. **Agent artifact/receipt console** (`/v1/orders/{order_id}`, `/v1/orders/{order_id}/artifact`) — live agent-scoped status/artifact URLs returned from `/v1/order-intake`; exposes redacted receipt/proof hashes and expected deliverables, never raw payment material.
11. **Checkout conformance profile/probe** (`/.well-known/ddg-agent-checkout-conformance.json`, `scripts/agent_checkout_conformance_probe.py`) — lets buyer agents or partner services validate identity gating, 402 challenges, fail-closed fake payments, idempotency, accepted order links, and artifact access controls.
12. **MPP activation guide** (`/.well-known/ddg-mpp-activation-guide.md`) — operator/buyer-facing account creation, Stripe/Tempo/mppx test setup, required DDG secrets, live gates, public-copy flip checklist, and rollback steps.

## Penny transaction smoke test

`POST /v1/tx-smoke-test` is the tiny paid-request endpoint. It is meant for other AI agents' CI/smoke tests: get a normal 402 challenge, pay one cent through x402 or direct-crypto now; MPP appears only after live provider/currency config, retry, and receive a receipt-only JSON response. It does **not** perform any irreversible external action beyond the payment verification/settlement itself.

## Ethereum/Reth privacy-node posture

The `/v1/ethereum/rpc` route is for accountless buyer-side Ethereum reads: DDG runs the Reth node/proxy, the buyer agent does not need an Infura/Alchemy/vendor account, and the edge still requires AI-agent identity. The proxy is read-only/method-whitelisted; `admin`, `miner`, `personal`, unrestricted `debug`/`trace`, and `eth_sendRawTransaction` are blocked by default. The free beta wrapper now includes:

- sync readiness gate: `DDG_ETH_RPC_REQUIRE_SYNCED=1` returns `503 reth_rpc_syncing` until `eth_syncing=false` and latest block is non-zero/current;
- fair-use timer: `DDG_ETH_RPC_FREE_MAX_CONCURRENT_USERS=4`, `DDG_ETH_RPC_FREE_LEASE_SECONDS=600`, `DDG_ETH_RPC_FREE_MAX_REQUESTS_PER_LEASE=30` by default;
- node overload guard: `DDG_ETH_RPC_MAX_CONCURRENT=2`, `DDG_ETH_RPC_MAX_BATCH=10`, bounded timeout/response bytes.

Public self-serve should wait for Reth execution sync, consensus non-optimistic status, and `DDG_RETH_RPC_URL` health through the payment edge.

## Protocol stance

- **x402**: live HTTP 402 payment flow for stablecoin-native agents and Bazaar-style discovery. The canonical `PAYMENT-REQUIRED` `accepts[]` advertises Base, Polygon, Arbitrum One, World Chain, and Solana mainnet USDC; Base mainnet USDC stays first for x402scan/CDP compatibility.
- **Direct crypto**: live receiving-address rail with automatic verification for verifier-supported assets and manual/operator-confirmed fallback for the rest of the public manifest. The public families are EVM/stablecoins, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, and XMR. ADA/Cardano is intentionally not advertised until a DDG-controlled address plus verification/manual-confirmation policy exists.
- **MPP**: code-ready and signer-key-ready, but not publicly claimed live until a real MPP/Tempo currency or Stripe SPT profile/env is configured, `ready:true` passes, a penny payment settles, idempotent replay passes, fake tokens fail closed, and the leak scan remains clean.

## AI-only sales posture

- Public self-serve and paid routes are AI-agent only.
- Human traffic without a stable agent identity header (X-Agent-Id / X-DDG-Agent-Id / X-DDG-User) is rejected with `403 agent_only`.
- We sell DDG-packaged inference and bounded artifacts, not raw model subscriptions/accounts.

## Model-router model aliases

Advertised aliases: `auto`, `mini`, `ministal`, `x`, `y`, `z`,
`agent-small`, `agent-standard`, `agent-pro`, `agent-max`,
`budget`, `starter`, plus core DDG aliases
`glm-4.5-air`, `glm-4.5`, `glm-4.6`, `glm-4.7`, `glm-5`,
`glm-5-turbo`, `glm-5.1`, `glm-5.2`, `gpt-5.3-codex-spark`, `gpt-5.3-codex`,
`gpt-5.4`, `gpt-5.5`, `claude-haiku-4.5`, `claude-sonnet-4.6`,
`claude-opus-4.8`.

`x_router.agent_profile` hints are also supported for non-advanced callers:
`low`/`budget`/`standard`/`pro`/`premium`.

Corrections from research:

- Z.AI docs list `GLM-4.5-Air`; I did not find an official `GLM-4.6-Air` page/pricing row.
- Anthropic docs list Claude Opus 4.8, Sonnet 4.6, and Haiku 4.5; I did not find official Sonnet 4.7 in the current docs.
- Claude Pro/Max subscription access should not be exposed to buyers. Claude aliases are for API-backed DDG application output only.
- GPT-5.3 Codex Spark/Codex naming and public API availability must be verified before broad sale; OpenAI Codex docs describe Spark as research-preview/Pro-only at launch.

## Model-router compliance stance

Do not sell raw API keys, auth tokens, or account seats. Do not market this as unrestricted resale of OpenAI/GLM/Claude accounts. The safer packaging is:

> Agents buy DDG-operated inference/agent-task outputs with budgets, receipts, abuse controls, and model-tier routing.

## Local inference/free-seat status — 2026-06-14

The live implementation can expose **up to two** free local-model seats when configured local runtime backends are healthy:

- Production target: two health-derived 8GB-VRAM local runtime seats, exposed only through the payment edge.
- `OLLAMA_API_URLS` should list private generation endpoints in deployment env only; do not publish raw backend URLs.
- `/v1/ollama-models` reports `local_free_seats.configured_free_seat_cap`, `healthy_local_seat_count`, and lease caps without exposing raw LAN URLs.
- Defaults are intentionally usable but bounded: 24-hour per-agent lease (`86400` seconds), 100 requests per lease, 60s swarm generation timeout, and 120s local `/v1/model/agent-run` timeout. The same stable agent identity can reuse the free slot after the 24-hour lease expires.
- `/v1/micro-model-swarm-preview` and local Ollama routes under `/v1/model/agent-run` use non-blocking per-backend seat locks, so one busy backend does not block another healthy configured backend.
- If only one backend is online, the catalog and lease pool drop to one seat; if none are healthy, generation returns a controlled unavailable/busy response.
- Raw local runtimes stay private behind the payment edge. Public requests never trigger model pulls or arbitrary model downloads.

Operational host/IP/GPU inventory belongs in private ops notes only, not in agent-consumed launch docs.

## Files

- `pricing.json` — canonical draft price catalog.
- `agent-catalog.json` — `.well-known` AI-agent catalog that summarizes discovery URLs, live routes, manual review offers, required headers, and safety posture.
- `quickstart.md` — concise agent-client onboarding/checklist for 403/402/idempotency/payment behavior, including recommended first order-intake packages and examples.
- `sales-launch-pack-2026-06-08.md` — customer-facing beta launch package sheet with first services to sell, copy, examples, and current caveats.
- `reth-ethereum-agent-rpc-analysis-2026-06-08.md` — decision note for planned Reth/Ethereum node access as an agent-facing blockchain intelligence/RPC product.
- `openapi.agent-services.json` — OpenAPI 3.1 discovery with MPP-style payment metadata.
- `agent-checkout-conformance-profile.json` — machine-readable 403/402/order-console/idempotency conformance profile exposed at `/.well-known/ddg-agent-checkout-conformance.json`.
- `mpp-tempo-stripe-account-activation-guide-2026-06.md` — step-by-step MPP/Tempo/Stripe account, env, smoke-test, go-live, and rollback guide exposed at `/.well-known/ddg-mpp-activation-guide.md`.
- `llms.txt` — agent-readable service catalog.
- `edge/payment_edge_scaffold.py` — payment edge with pluggable verification adapters. Production uses provider-backed verification; mock tokens are development-only and must remain disabled in systemd production env.
- `scripts/operator_queue_digest.py` — safe operator digest builder for queued paid-agent orders; writes Telegram-ready markdown but does not send or fulfill anything automatically.
- `scripts/agent_checkout_conformance_probe.py` — non-spending by default checkout probe; with dev mock/real payment credentials it validates accepted order links, artifact/status access controls, and idempotency behavior.
- `edge/agent_runners.py` — sandbox-conscious subprocess wrappers for env-gated Kimi/Claude operated artifact routes.
- `mcp/README.md` and `mcp/ddg-agent-swarm-mcp-design.md` — MCP quickstart/design for AI-agent swarms that want service discovery, quotes, paid model runs, order intake, security-service catalog access, and one-cent transaction smoke tests.
- `edge/mpp_verifier_sidecar.mjs` — seller-side MPP verifier sidecar using `mppx/server`; requires recipient, currency, and a Tempo server signing account for real settlement.
- `edge/x402_verifier_sidecar.py` — x402 verifier/settle adapter translating the Python edge's generic payment payload into facilitator `paymentPayload` / `paymentRequirements` calls.
- `edge/direct_crypto_verifier_sidecar.py` — public-chain direct-crypto verifier sidecar for BTC/LTC/DOGE/BCH/ZEC, EVM native transfers, and USDC on Ethereum/Base/Polygon; unsupported chains fail closed to manual confirmation.
- `payment-provider-and-waf-runbook-2026-06-05.md` — setup walkthrough for MPP/x402 verifier URLs, direct crypto/manual fallback, and free Cloudflare 1010 alternatives.
- `deploy/two-host-local-ai-production-runbook.md` — private deployment checklist for the two free local AI seats, lease policy, runtime status, and post-sync verification.
- `direct_crypto_addresses.public.json` / `direct_crypto_addresses.env` — public direct-crypto receiving manifest for EVM/stablecoins, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, and XMR.
- `audit/preservation_snapshot.md` — branch/status snapshot taken before launch edits.

## Local scaffold smoke test

```bash
python3 sales_artifacts/agent_payments/edge/payment_edge_scaffold.py --port <local-edge-port>

curl -i http://LOCAL_EDGE/llms.txt
curl -i -X POST http://LOCAL_EDGE/v1/model/chat-completions \
  -H 'content-type: application/json' \
  -H 'X-Agent-Id: demo-agent-id' \
  -d '{"model":"glm-5-turbo","messages":[{"role":"user","content":"hello"}]}'

curl -i -X POST http://LOCAL_EDGE/v1/model/chat-completions \
  -H 'content-type: application/json' \
  -H 'Idempotency-Key: demo-1' \
  -H 'Authorization: Payment mock-valid' \
  -H 'X-Agent-Id: demo-agent-id' \
  -d '{"model":"glm-4.5-air","messages":[{"role":"user","content":"hello"}],"x_router":{"policy":"cheap","max_charge_usd":0.25}}'
```



## Payment verification modes

The scaffold now supports automated payment verification plus a manual crypto fallback:

- `mock` (development): accepts only mock headers when mocked token mode is enabled.
- `provider` (production-ready): delegates payment claim validation to an external verifier endpoint.

Set via: `DDG_PAYMENT_VERIFICATION_MODE={mock|provider|disabled}`.
If unset, the mode defaults to `mock` when `PAYMENT_EDGE_ALLOW_MOCK_TOKENS=1`, otherwise `provider`.

Provider verifier endpoints:

- `DDG_PAYMENT_MPP_VERIFY_URL` (or `MPP_VERIFY_URL`)
- `DDG_PAYMENT_X402_VERIFY_URL` (or `X402_VERIFY_URL`)
- `DDG_PAYMENT_X402_SETTLE_URL` (optional x402 settle call after verify)
- `DDG_PAYMENT_DIRECT_CRYPTO_VERIFY_URL` (optional direct-crypto automatic proof verifier; when absent, direct crypto remains manual-confirmation beta)

Sidecar smoke stack:

```bash
# direct crypto
python sales_artifacts/agent_payments/edge/direct_crypto_verifier_sidecar.py --host <local-host> --port <direct-crypto-port>

# x402 public/testnet adapter
set -a; . sales_artifacts/agent_payments/direct_crypto_addresses.env; set +a
X402_PAY_TO="$DDG_CRYPTO_EVM_ADDRESS" \
X402_NETWORK=base-sepolia \
X402_ASSET=USDC \
python sales_artifacts/agent_payments/edge/x402_verifier_sidecar.py --host <local-host> --port <x402-port>

# MPP; real settlement additionally needs MPP_TEMPO_PRIVATE_KEY and MPP_SECRET_KEY
cd sales_artifacts/agent_payments
MPP_RECIPIENT_ADDRESS="$DDG_CRYPTO_EVM_ADDRESS" \
MPP_CURRENCY=0x20c0000000000000000000000000000000000000 \
MPP_CHARGE_AMOUNT=0.01 \
node edge/mpp_verifier_sidecar.mjs
```

Run the edge against all three:

```bash
DDG_PAYMENT_VERIFICATION_MODE=provider \
DDG_PAYMENT_DIRECT_CRYPTO_VERIFY_URL=http://LOCAL_DIRECT_CRYPTO/verify \
DDG_PAYMENT_X402_VERIFY_URL=http://LOCAL_X402/verify \
DDG_PAYMENT_X402_SETTLE_URL=http://LOCAL_X402/settle \
DDG_PAYMENT_MPP_VERIFY_URL=http://LOCAL_MPP/verify \
DDG_REQUIRE_AGENT_ID=1 \
python sales_artifacts/agent_payments/edge/payment_edge_scaffold.py --port <local-edge-port>
```

Verified controlled-failure behavior: health returns 200, missing agent identity returns `403 agent_only`, unpaid/fake MPP/fake x402/fake direct-crypto requests return app-layer `402 payment_required` instead of `503 payment_verification_unavailable`.

Optional auth headers:
- `DDG_PAYMENT_MPP_VERIFY_TOKEN` / `DDG_PAYMENT_X402_VERIFY_TOKEN`

Expected verifier response JSON fields:
- `valid: true` (or `ok: true`)
- optional `receipt`, `payer`, `amount_usd`

If production mode is enabled but no verifier URL is configured, paid routes return `503 payment_verification_unavailable`.

### Direct crypto automatic proof + manual fallback

Coinbase/CDP x402 is deferred for now. Initial beta can publish configured direct-payment addresses in the 402 body:

```bash
DDG_CRYPTO_EVM_ADDRESS=0x...
DDG_CRYPTO_BTC_ADDRESS=bc1...
DDG_CRYPTO_BCH_ADDRESS=bitcoincash:...
DDG_CRYPTO_LTC_ADDRESS=ltc1...
DDG_CRYPTO_DOGE_ADDRESS=D...
DDG_CRYPTO_SOL_ADDRESS=...
DDG_CRYPTO_TRX_ADDRESS=T...
DDG_CRYPTO_XRP_ADDRESS=r...
DDG_CRYPTO_XLM_ADDRESS=G...
DDG_CRYPTO_ALGO_ADDRESS=...
DDG_CRYPTO_DOT_ADDRESS=1...
DDG_CRYPTO_XMR_ADDRESS=...
DDG_CRYPTO_ZEC_ADDRESS=...
```

EVM covers ETH-compatible assets plus major EVM stablecoins (`USDC`, `USDT`, `DAI`, `PYUSD`, `FRAX`, `FDUSD`, `GUSD`, `LUSD`, `USDP`, `TUSD`, `EURC`) across supported EVM networks. SOL/TRX/XLM/ALGO entries cover chain-specific stablecoin variants where those addresses are configured.

Agents can retry paid requests with an automatic proof header when `DDG_PAYMENT_DIRECT_CRYPTO_VERIFY_URL` is configured:

```http
X-Direct-Crypto-Proof: {"asset":"BCH","network":"bitcoin-cash","txid":"...","amount":"0.05"}
```

Without a direct-crypto verifier URL, agents submit `payment_proof` on `/v1/order-intake` for operator confirmation.

Generated public addresses now live in: