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

```text
sales_artifacts/agent_payments/direct_crypto_addresses.public.json
sales_artifacts/agent_payments/direct_crypto_addresses.env
```

Private keys/mnemonics were generated under `c_priv/` with 0700/0600 permissions; that directory is gitignored and must be backed up offline before accepting real payments.

```json
{"payment_proof":{"asset":"BTC","network":"bitcoin","txid":"...","amount":"0.01"}}
```

The queue stores only a hash of proof metadata and waits for operator confirmation before fulfillment.

### App-layer rate limits

The payment edge now applies per-path/per-agent rate limits before paid/free dispatch:

```bash
DDG_RATE_LIMIT_ENABLED=1
DDG_RATE_LIMIT_WINDOW_SECONDS=60
DDG_RATE_LIMIT_MAX_REQUESTS=60
```

Tune lower for the free swarm if public abuse starts.

### Cloudflare 1010/Bot-check diagnostic

Use `edge/check_cloudflare_403.py` before deployment claims:

```bash
DDG_CF_PATHS="/health,/openapi.json,/v1/model/chat-completions" \
  DDG_CF_TIMEOUT_SECONDS=6 \
  python sales_artifacts/agent_payments/edge/check_cloudflare_403.py
```

Observed in this environment: default urllib requests are challenged with 1010, while browser-like/explicit Hermes UAs are allowed.

## Production gates

- Unpaid request returns 402 and does not call Hermes/model providers.
- Invalid payment rejected.
- Valid MPP and x402 requests accepted.
- Duplicate idempotency key does not execute twice.
- Direct Hermes backend remains localhost/internal-key only.
- Secrets are not logged.
- Human approval remains on outreach/spend side effects.

## AI-agent model-query launch policy

- DDG sells AI-agent-queryable model outputs and bounded artifact runs, not raw provider OAuth/account/session/token access.
- Eligible launch model routes are priced at 75% of comparable official API list pricing where DDG can fulfill through available backend capacity.
- Account-backed coding/model capacity is DDG-operated only: buyers receive outputs/artifacts and receipts; credentials and sessions stay private.
- Riskier account-backed artifact runs remain manual/operator-reviewed until provider terms and production controls are sufficient for self-serve use.


## Free local model seats

Downloaded Ollama models are discoverable at `/v1/ollama-models` and usable through `/v1/micro-model-swarm-preview` with a rotating lease timer. Local Ollama `/v1/model/agent-run` routes are also **free for a limited time** as best-effort/no-SLA capacity. After the promo, only local models **4B and smaller** remain free; larger local models become paid or operator-approved capacity.

Agents can request a new local model/runtime at `/v1/ollama-model-request` using `runtime=ollama`, `runtime=llama.cpp`, or `runtime=lm_studio`. Public requests queue operator review and never auto-download models/GGUFs. Default guardrails reserve disk headroom and cap ordinary public requests unless an operator explicitly approves a larger pull. Prefer durable backend storage for large pulls and preserve operator workstation headroom for chain/node workloads.

## DDG free local-model agent slots — exact rollout menu

Limited-time launch offer: AI agents can connect to DDG local-model slots for **$0** via `/v1/micro-model-swarm-preview` and local Ollama routes under `/v1/model/agent-run`. Public catalog: `/v1/ollama-models` and `/.well-known/ddg-ollama-models.json`.

DDG exposes both native model context and service context honestly: large GGUF aliases are created with DDG free-slot `num_ctx=32,768` by default even when the native GGUF metadata supports 131K, 202K, 262K, or 1M context.

Priority A/B rollout models:
- `mradermacher/huihui-gemma4-12b-ablit:q4_k_m` — 12B Q4_K_M; native ctx 131,072; DDG free-slot ctx 32,768; Gemma-family abliterated route.
- `mradermacher/mistral-nemo-heretic-12b:q4_k_m` — 12B Q4_K_M; native ctx 1,024,000; DDG free-slot ctx 32,768; Mistral-Nemo 12B uncensored/heretic long-context route.
- `mradermacher/dolphin3-llama31-8b-ablit:q4_k_m` — 8B Q4_K_M; native ctx 131,072; DDG free-slot ctx 32,768; Dolphin/Llama3.1 abliterated general route.
- `mradermacher/huihui-glm47-flash-ablit:iq3_xs` — GLM-4.7 Flash class IQ3_XS; native ctx 202,752; DDG free-slot ctx 32,768; GLM-family abliterated route; IQ3 chosen for 8GB-class hosts.
- `mradermacher/huihui-qwen3-coder-30b-a3b-ablit:iq3_xs` — 30B-A3B IQ3_XS; native ctx 262,144; DDG free-slot ctx 32,768; Qwen coder sparse/active-parameter abliterated experiment.
- `mradermacher/qwen36-27b-heretic:q4_k_s` — 27B Q4_K_S; native ctx 262,144; DDG free-slot ctx 32,768; Larger Qwen3.6 uncensored/heretic route.
- `mradermacher/qwen36-35b-a3b-ablit:iq3_xs` — 35B-A3B IQ3_XS; native ctx 262,144; DDG free-slot ctx 32,768; Large abliterated MoE-style Qwen3.6 experiment.
- `mradermacher/dolphin-mistral-24b-venice:iq3_xs` — 24B IQ3_XS; native ctx 32,768; DDG free-slot ctx 32,768; Dolphin/Mistral Venice-style route.

Post-promo policy: <=4B local models remain free; >4B local routes become paid/operator-approved capacity. Public model requests never auto-download; use `/v1/ollama-model-request` and DDG operator review.

## Kimi K2.7, MCP, and AI-agent cybersecurity offers

- `kimi-code/k2.7` is exposed as **Kimi K2.7 Code** through `/v1/model/agent-run` when `DDG_ENABLE_KIMI_AGENT_RUN=1`. Public wording: "Kimi K2.7 Code is available as a DDG-operated paid artifact/result route and can be used within Kimi Code."
- The DDG agent-swarm MCP design lives at `mcp/ddg-agent-swarm-mcp-design.md`; the initial stdio server skeleton is `mcp/ddg_agent_services_mcp_server.py`.
- The cybersecurity service catalog lives at `cybersecurity-services.json` and covers prompt-injection, npm/Python dependency risk, API-key/secret leakage, malware triage, and MCP/tool security audits.

## Verification & Heartbeat services (E25/E26)

| `verify_claim` | ``$0.01`` | Deterministic claim-vs-source verification (CVE real? package vulnerable/exists? domain resolves? TLS cert valid? URL reachable?) against authoritative sources (NVD/CVE.org, OSV.dev, PyPI/npm, DNS, TLS). Boolean verdict + evidence snapshot; no LLM anywhere. |
| `verify_action` | ``$0.01`` | Post-action side-effect verification: deterministically re-read a claimed real-world state (HTTP JSON endpoint fields, status code) and compare to expected. Answers did-it-actually-happen independent of the acting agent's narration. |
| `resolve_outcome` | ``$0.01`` | Timeout-outcome resolution: idempotency-keyed verdict replay without re-executing anything (TTL-cached). Ends double-execution and blind-retry loops after tool-call timeouts. |
| `verify_schema_drift` | ``$0.01`` | API-contract drift probe: fingerprint the live OpenAPI/JSON doc (sorted path/method list, sha256) vs pinned. Verdict match|drifted|unreachable + current fingerprint. |
| `verify_rules` | `free` | Machine-readable rule catalog for all verification check types (input shapes, evidence schema, limits). Free. |
| `heartbeat_register` | ``$0.01`` | Register a heartbeat watch for an agent URL ($0.01 per 30-day window): bounded prober re-checks on your interval (300s..24h); alive->dark / dark->alive / flap alerts, optional HMAC-signed webhook delivery. |
| `heartbeat_status` | ``$0.01`` | Watch state: last verdict, last probe time, consecutive fails, uptime_30d and uptime_all_time ratios, alert count. |
| `heartbeat_alerts` | `free` | Read your own watch's alerts (went_dark|back_alive|flap). Webhook-protected watches require webhook_secret. Free. |
| `heartbeat_leaderboard` | ``$0.01`` | Highest-uptime watched agents (>= min_probes), uptime ratios and probe counts. |
| `heartbeat_rules` | `free` | Machine-readable heartbeat config contract (interval bounds, expect shapes, caps, alert kinds, webhook signing). Free. |

## Compliance & Facts services (E28/E29)

| `sanctions_screen` | ``$0.01`` | Sanctions screen with PINNED list versions (OFAC SDN + EU list): verdict clear|match + per-list version/rows/matches. Signed receipt. |
| `sanctions_delta` | ``$0.01`` | Sanctions DELTA feed since YYYY-MM-DD (OFAC recent actions). Signed. |
| `preflight_402` | ``$0.01`` | x402 challenge compliance pre-flight: verdict an endpoint's 402 envelope against v1/v2 + MPP shape rules. Signed. |
| `drainer_check` | ``$0.01`` | Wallet/URL drainer & abuse check (Chainabuse): reported|no_reports + scam types. Signed. |
| `ucp_verify` | ``$0.01`` | UCP conformance verifier: /.well-known/ucp manifest fetch + spec-rule verdict. Signed. |
| `ucp_spec` | `free` | Machine-readable UCP check summary. Free. |
| `macro_latest` | ``$0.01`` | Latest official macro print (cpi|nfp|unemployment) from BLS. Signed. |
| `macro_series` | `free` | Supported macro series catalog. Free. |

## Agent Primitives services (Wave 2, E31-E38)

| `ap2_verify_mandates` | ``$0.01`` | AP2 mandate verifier: verify a pair of AP2 SD-JWT+KB checkout/payment mandates (signature, key binding, disclosures, constraints vs terms) and get a signed verdict + dispute-ready evidence. |
| `ap2_verify_single` | ``$0.01`` | AP2 single-mandate verifier: parse + verify one SD-JWT+KB payment mandate (signature, disclosures, expiry, key binding). Signed verdict. |
| `ap2_spec` | `free` | AP2 verifier spec: accepted vct types, constraint checks, rules, verdicts. Free. |
| `escrow_condition` | ``$0.01`` | Escrow-condition oracle (NO custody): deal spec + evidence -> signed release|refund|extend verdict for x402-v2/MPP-session/hash-lock escrows. |
| `escrow_dispute_period` | ``$0.01`` | Escrow dispute-window clock: opened_at + period vs evaluation time -> dispute_open|dispute_expired. Signed verdict. |
| `escrow_rules` | `free` | Escrow oracle: supported escrow types, condition kinds, evidence shapes, rules. Free. |
| `export_verdict` | ``$0.01`` | Export-control verdict: ECCN x destination -> license_required|no_license_required with rule-table version + optional live Entity-List cross-check. Signed. |
| `export_exceptions` | ``$0.01`` | Export-control license-exception finder: ECCN x destination -> ranked applicable exceptions (NAC/TMP/RPL/GOV/TSR/SVC/BAG/AVS/STA). Signed. |
| `export_rule_table_version` | `free` | Export rule-table version + row count + categories. Free. |
| `export_destinations` | `free` | Export D-group/E-group destination reference. Free. |
| `markets_snapshot` | ``$0.01`` | Cross-venue prediction-market matched snapshot: Polymarket+Kalshi+Manifold+PredictIt -> matched questions, cross-venue spread, consensus probability. Signed. |
| `markets_spread` | ``$0.01`` | Best cross-venue prediction-market match for a query: spread % + arbitrage note + per-venue prices. Signed. |
| `markets_venues` | `free` | Supported prediction-market venues + price semantics. Free. |
| `markets_health` | `free` | Per-venue prediction-market API reachability. Free. |
| `payroll_ledger` | ``$0.01`` | Sub-agent payroll ledger: normalize payment proofs (x402/MPP/AP2/manual) into per-sub-agent spend ledger + anomaly alerts. Signed export. |
| `payroll_cap_check` | ``$0.01`` | Payroll budget gate: under_cap|over_cap verdict for a coordinator/sub-agent vs cap using recorded ledger rows. Signed. |
| `payroll_ledger_summary` | `free` | Read-only per-sub-agent payroll rollup for a coordinator. Free. |
| `payroll_rules` | `free` | Payroll lane: proof schema, alert rules, cap semantics. Free. |
| `bridge_health` | ``$0.01`` | Bridge-health composite: exploit history (DefiLlama) + TVL component -> healthy|elevated_risk|exploit_history signed verdict. |
| `bridges_exploits` | `free` | Recent bridge exploits from DefiLlama hacks dataset. Free. |
| `bridges_rules` | `free` | Bridge-health rules + verdict semantics + alias map. Free. |
| `bounty_verify_deliverable` | ``$0.01`` | Neutral bounty-fulfillment verification: bounty spec vs submitted deliverable -> conformant|non_conformant signed verdict (hash/commit/signed-outcome). |
| `bounty_payout_manifest` | ``$0.01`` | Bounty payout-manifest builder: winners vs pot -> validated, deduped, per-recipient signed instruction rows. No custody. |
| `bounty_rules` | `free` | Bounty lane conformance + manifest validation rules. Free. |
| `bounty_proof_schema` | `free` | Exact accepted request shapes for bounty verification + manifests. Free. |
| `llm_audit_bill` | ``$0.01`` | LLM bill line-item audit: usage rows vs source-published pricing (OpenRouter, 24h cache) -> bill_correct|overcharge|undercharge + per-row math. Signed. |
| `llm_price_lookup` | ``$0.01`` | Published LLM pricing lookup (OpenRouter): per-token + per-1M USD rates for a model. Signed. |
| `llm_audit_rules` | `free` | LLM audit lane: tolerance rules, cache semantics, supported providers. Free. |
