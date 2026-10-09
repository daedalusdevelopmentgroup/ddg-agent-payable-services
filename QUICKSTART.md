# DDG paid-agent quickstart

Base URL: `https://agents.daedalusdevelopmentgroup.com`

Pay-per-call AI agent services gateway: one x402/direct-crypto entry point for callable tools, OpenAI-compatible routes, readiness audits, MCP security checks, discovery repair, receipts, and proof artifacts.

This API is for AI-agent callers only. Humans or scripts without an agent identity header are rejected before payment handling.

Current surface: **109 services** exposed as **114 OpenAPI operations**: **90 paid x402/direct-crypto operations** and **24 intentionally free discovery/utility operations**.

MCP one-liner:

```bash
DDG_MCP_AGENT_ID=your-agent uvx --from ddg-agent-services-mcp ddg-agent-services-mcp
```

## Fast path for buyer agents

1. Start with `/v1/tx-smoke-test` for a `$0.01` paid receipt proof.
2. Try `/v1/site-audit` for a `$0.03` read-only artifact.
3. Use `/v1/chat/completions`, `/v1/models`, or `/v1/embeddings` for OpenAI-compatible gateway calls.
4. Buy `/v1/agent-readiness-scorecard` or `/v1/agent-discovery-pack` for `$0.01` when a service needs better machine-readable discovery.
5. Buy `/v1/agent-payment-readiness-audit` or `/v1/mcp-tool-security-audit` for `$0.02` when the service needs paid-agent or MCP security hardening.

Recommended starting budget: `$1` is enough to test the one-cent smoke route, the low-cost site audit, and several free discovery/utility calls.

## Discover

```bash
curl https://agents.daedalusdevelopmentgroup.com/.well-known/ai
curl https://agents.daedalusdevelopmentgroup.com/.well-known/api-catalog
curl https://agents.daedalusdevelopmentgroup.com/.well-known/agent-skills/index.json
curl https://agents.daedalusdevelopmentgroup.com/.well-known/agents.json
curl https://agents.daedalusdevelopmentgroup.com/.well-known/agent-catalog.json
curl https://agents.daedalusdevelopmentgroup.com/llms.txt
curl https://agents.daedalusdevelopmentgroup.com/openapi.json
curl https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json
```

## Required request headers

- `X-Agent-Id` (preferred), `X-DDG-Agent-Id`, or `X-DDG-User`
- `Idempotency-Key` for retried POST requests
- Payment after a `402`: `Payment-Signature` / `X-PAYMENT` for x402 (Base, Polygon, Arbitrum One, World Chain, and Solana mainnet USDC), or direct-crypto proof headers/body using one of the public receiving-address families (EVM/stablecoins, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, and XMR). `Authorization: Payment ...` for MPP is accepted only when the public 402 challenge explicitly advertises MPP.

## Expected gate sequence

1. Missing identity => `403 agent_only`.
2. Identity present but no valid payment => `402 payment_required` with payment options.
3. Valid settled payment/proof => route executes or queues an operator-reviewed order.
4. Reusing an idempotency key with a different body => `409 idempotency_conflict`.
5. Paid/manual order-intake success => `202` with `order_id`, `status_url`, `artifact_url`, and `receipt_console_url`.
6. Polling `GET /v1/orders/{order_id}` or `/artifact` with a different agent identity => `403 order_not_authorized`.

## Minimal unpaid challenge probe

```bash
curl -i -X POST https://agents.daedalusdevelopmentgroup.com/v1/order-intake \
  -H 'content-type: application/json' \
  -H 'X-Agent-Id: your-agent-id' \
  -H 'Idempotency-Key: order-probe-001' \
  -d '{"service_id":"lead_pack_micro","target":{"url":"https://example.com"}}'
```

## Order status and artifact console

Every accepted `/v1/order-intake` response now returns agent-readable links:

- `status_url` / `receipt_console_url`: `GET /v1/orders/{order_id}`
- `artifact_url`: `GET /v1/orders/{order_id}/artifact`

Poll with the **same stable agent identity** used at intake. The status response returns redacted metadata only: order id, service id, queue status, payment status, receipt/proof hashes, expected deliverables, and artifact links. Raw payment tokens, raw direct-crypto proof payloads, provider credentials, and buyer contact are never returned.

```bash
curl -i https://agents.daedalusdevelopmentgroup.com/v1/orders/ddg-order-example1234 \
  -H 'X-Agent-Id: your-agent-id'

curl -i https://agents.daedalusdevelopmentgroup.com/v1/orders/ddg-order-example1234/artifact \
  -H 'X-Agent-Id: your-agent-id'
```

Artifacts that are not ready return `202` plus `Retry-After`; completed artifacts return JSON or Markdown.

## Checkout conformance profile/probe

Agents and partner services can discover the expected checkout contract at:

```bash
curl https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-checkout-conformance.json
```

Strict refund/reversal policy is exposed separately so buyer agents can verify that refunds cannot leave paid entitlements live:

```bash
curl https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-refund-policy.json
```

For local/dev or intentional paid-provider validation, run:

```bash
python3 sales_artifacts/agent_payments/scripts/agent_checkout_conformance_probe.py \
  --base-url https://agents.daedalusdevelopmentgroup.com \
  --agent-id buyer-agent-example
```

Without a credential flag, the probe is non-spending and verifies only identity gate, payment challenge, and fake-token fail-closed behavior. With a dev mock or real credential, it also verifies order console links, same-agent status, other-agent 403, artifact pending/ready behavior, and idempotency replay/conflict.

## One-cent transaction smoke test

Use this when another AI agent wants a minimal paid-call smoke test. First call without payment to receive the 402 challenge, then retry with the chosen payment proof/signature.

```bash
curl -i -X POST https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test \
  -H 'content-type: application/json' \
  -H 'X-Agent-Id: your-agent-id' \
  -H 'Idempotency-Key: penny-smoke-001' \
  -d '{"request_label":"agent-ci-payment-smoke"}'
```

Success returns `service: tx_penny_smoke_test`, `amount_usd: "0.01"`, and payment receipt headers.

## Model/provider-backed artifact runs

For normal model use, AI agents should call `/v1/model/chat-completions` for basic conversation/analysis/code-help prompts with `x_router.max_charge_usd`. For longer bounded work, call `/v1/model/agent-run` where the route is enabled, or queue `service_id=provider_model_artifact_order` through `/v1/order-intake`. DDG sells the result/artifact only; it does not sell raw auth tokens, account seats, provider credentials, or unrestricted model account access.

### Free local model promo

Local runtime routes under `/v1/micro-model-swarm-preview` and `/v1/model/agent-run` are **free for a limited time** as best-effort/no-SLA capacity. Agents can choose among Ollama, llama.cpp, and LM Studio/llmster when the requested model is listed healthy in `/v1/ollama-models`:

- route prefix: `ollama/<model>`, `llama.cpp/<model>`, or `lm_studio/<model>`
- or request fields: `{ "model": "...", "runtime": "ollama|llama.cpp|lm_studio" }`

After the promo, only local models **4B and smaller** remain free; larger local models move to paid/operator-approved capacity. Discover current runtime/model availability at `/v1/ollama-models`.

Agents can request local models/runtimes through `/v1/ollama-model-request`:

```bash
curl -i -X POST https://agents.daedalusdevelopmentgroup.com/v1/ollama-model-request \
  -H 'content-type: application/json' \
  -H 'X-Agent-Id: your-agent-id' \
  -d '{"model":"mradermacher/Huihui-gemma-4-12B-it-abliterated-GGUF:Q4_K_M","runtime":"llama.cpp","expected_size_gb":7,"reason":"need a 12B abliterated GGUF route"}'
```

Requests queue operator review only; public requests never auto-download. Default guardrails reserve 300GiB disk and cap ordinary public model requests at 25GiB unless an operator approves a larger pull. Prefer durable runtime backend storage for large models so overflow runtime backend keeps Reth sync headroom.

## Free AI skill safety scan

Use this before installing or sharing a third-party agent skill/workflow. The launch scanner is free, static-only, and does **not** execute code or fetch remote URLs; it flags prompt-injection, credential-exfiltration, dangerous tool-use, install-script/package-lifecycle, and broad file/network access red flags.

```bash
curl -i -X POST https://agents.daedalusdevelopmentgroup.com/v1/ai-skill-safety-scan \
  -H 'content-type: application/json' \
  -H 'X-Agent-Id: your-agent-id' \
  -d '{"skill_markdown":"# Skill\nUse tools only within the declared scope."}'
```

## Ethereum private Reth RPC plan

`/v1/ethereum/rpc` now has the free launch-beta wrapper we need: AI-agent identity gate, read-only method whitelist, sync-readiness gate, per-agent fair-use lease timer, per-lease request cap, max batch size, response byte cap, and upstream max-concurrent request cap. It should **not** be marketed as public-ready until overflow runtime backend Reth reports `eth_syncing=false`, `eth_blockNumber` is non-zero/current, and Lighthouse is no longer optimistic.

Default free/fair-use controls:

- `DDG_ETH_RPC_FREE_MAX_CONCURRENT_USERS=4`
- `DDG_ETH_RPC_FREE_LEASE_SECONDS=600`
- `DDG_ETH_RPC_FREE_MAX_REQUESTS_PER_LEASE=30`
- `DDG_ETH_RPC_MAX_CONCURRENT=2`
- `DDG_ETH_RPC_MAX_BATCH=10`
- `DDG_ETH_RPC_TIMEOUT_SECONDS=8`
- `DDG_ETH_RPC_REQUIRE_SYNCED=1`

Example once synced:

```bash
curl -i -X POST https://agents.daedalusdevelopmentgroup.com/v1/ethereum/rpc \
  -H 'content-type: application/json' \
  -H 'X-Agent-Id: buyer-agent-example' \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'
```

## Manual/beta order-intake

`/v1/order-intake` records redacted metadata and requires operator review for manual services such as lead packs, browser proofs, outreach briefs, MCP audits, local-business demo packs, payment-readiness audits, repo context packs, and schema/tool repair. Outreach-send or external-account actions are never automatic.

Recommended first paid packages:

| service_id | Price | Use when |
| --- | ---: | --- |
| `tx_penny_smoke_test` | `$0.01` | An agent wants to test its ability to complete a paid DDG transaction and receive a receipt. Use direct endpoint `/v1/tx-smoke-test`. |
| `provider_model_artifact_order` | `$0.01` | An agent wants DDG-operated model/artifact work with receipts and no raw account/token access transferred. |
| `ethereum_private_rpc_query` | `$0.01` | An agent wants read-only Ethereum/Base RPC data without its own RPC vendor account. |
| `local_business_demo_pack` | `$0.02` | An agent wants a lead-specific staged demo concept and offer angle for a local business. |
| `agent_payment_readiness_audit` | `$0.02` | An agent/service builder wants x402/direct-crypto/MPP-readiness/402/idempotency/discovery reviewed. |
| `mcp_tool_server_build` | `$0.02` | An agent wants a small MCP tool/server scaffold with schema, install docs, and smoke tests. |
| `agent_tool_schema_repair` | `$0.02` | An agent has OpenAPI/MCP/tool schemas that are hard for agents to call reliably. |
| `repo_context_pack` | `$0.02` | An agent wants a repo/docs/SOP corpus turned into an agent-ready context pack or workflow. |

### Example: local-business demo pack

```bash
curl -i -X POST https://agents.daedalusdevelopmentgroup.com/v1/order-intake \
  -H 'content-type: application/json' \
  -H 'X-Agent-Id: buyer-agent-example' \
  -H 'Idempotency-Key: demo-pack-001' \
  -d '{
    "service_id":"local_business_demo_pack",
    "target":{"business_name":"Example Roofing Co","url":"https://example.test","location":"Boca Raton, FL"},
    "deliverable_preferences":{"format":"markdown_brief_plus_mockup_outline","include_outreach_angle":true}
  }'
```

### Example: agent payment-readiness audit

```bash
curl -i -X POST https://agents.daedalusdevelopmentgroup.com/v1/order-intake \
  -H 'content-type: application/json' \
  -H 'X-Agent-Id: buyer-agent-example' \
  -H 'Idempotency-Key: payment-audit-001' \
  -d '{
    "service_id":"agent_payment_readiness_audit",
    "target":{"url":"https://api.example.com","openapi_url":"https://api.example.com/openapi.json"},
    "scope":["402 semantics","idempotency","receipts","agent discovery","abuse limits"]
  }'
```

### Example: MCP tool/server build

```bash
curl -i -X POST https://agents.daedalusdevelopmentgroup.com/v1/order-intake \
  -H 'content-type: application/json' \
  -H 'X-Agent-Id: buyer-agent-example' \
  -H 'Idempotency-Key: mcp-build-001' \
  -d '{
    "service_id":"mcp_tool_server_build",
    "target":{"goal":"Expose read-only inventory lookup and order status tools for my agent workflow"},
    "deliverable_preferences":{"language":"python","include_smoke_tests":true,"include_install_docs":true}
  }'
```

## Ethereum/Reth node access status

Ethereum/Reth access is **not a live public service yet**. Current recommendation is to package it first as an agent-friendly blockchain intelligence/payment-verification product, not raw unrestricted RPC resale. See `reth-ethereum-agent-rpc-analysis-2026-06-08.md`.

## Model-query launch policy

- DDG sells AI-agent-queryable model outputs and bounded artifact runs, not raw provider OAuth/account/session/token access.
- Eligible launch model routes are priced at 75% of comparable official API list pricing where DDG can fulfill through available backend capacity.
- Account-backed coding/model capacity is DDG-operated only: buyers receive outputs/artifacts and receipts; credentials and sessions stay private.
- Riskier account-backed artifact runs remain manual/operator-reviewed until provider terms and production controls are sufficient for self-serve use.

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

## Verification & heartbeat (new)

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

## Compliance & Facts (E28/E29)

| `sanctions_screen` | ``$0.01`` | Sanctions screen with PINNED list versions (OFAC SDN + EU list): verdict clear|match + per-list version/rows/matches. Signed receipt. |
| `sanctions_delta` | ``$0.01`` | Sanctions DELTA feed since YYYY-MM-DD (OFAC recent actions). Signed. |
| `preflight_402` | ``$0.01`` | x402 challenge compliance pre-flight: verdict an endpoint's 402 envelope against v1/v2 + MPP shape rules. Signed. |
| `drainer_check` | ``$0.01`` | Wallet/URL drainer & abuse check (Chainabuse): reported|no_reports + scam types. Signed. |
| `ucp_verify` | ``$0.01`` | UCP conformance verifier: /.well-known/ucp manifest fetch + spec-rule verdict. Signed. |
| `ucp_spec` | `free` | Machine-readable UCP check summary. Free. |
| `macro_latest` | ``$0.01`` | Latest official macro print (cpi|nfp|unemployment) from BLS. Signed. |
| `macro_series` | `free` | Supported macro series catalog. Free. |

## Agent Primitives (Wave 2, E31-E38)

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

## Discovery Sequencer (free)

Point planning agents at the sequenced catalog instead of scanning flat lists:

- GET /v1/discovery/index (free) - Sequenced discovery index: all services grouped by category with composition seams (related routes) for planning agents.

- GET /v1/discovery/chunk (free) - Paginated discovery chunk: one category slice per read (?category=<cat>&cursor=<int>&limit=<int>) for bounded concurrent crawls.

- GET /.well-known/ddg-discovery-index.json (free) - Static sequenced catalog mirror for crawlers that want one well-known URL.

Chunk reads keep concurrent crawlers bounded: fetch only the categories you need.

## Spend & Subscription lanes (Wave 3, E40-E45)

| `v1_spend_policy_check` | ``$0.01`` | Check a candidate transaction against an agent spend policy; signed allow|deny|needs_approval verdict with fired rule and headroom. |
| `v1_spend_policy_rules` | `free` | List spend-policy verdict rules, fired-rule codes, the rails enum, and accepted request shapes. |
| `v1_spend_anomaly_rules` | `free` | Return the spend-anomaly rule names, thresholds, verdicts, and transaction-row schema. |
| `v1_spend_anomaly_scan` | ``$0.01`` | Signed stateless anomaly verdict over an agent transaction log: spikes, merchant concentration, overnight volume, vendor drift, burn-rate, duplicates. |
| `v1_spend_rail_compare` | ``$0.01`` | Compare net cost per payment rail for an amount and return the cheapest-rail verdict. |
| `v1_spend_rail_rules` | `free` | Return the rail fee table, rules, table version, and source docs. |
| `v1_model_telemetry_probe` | ``$0.01`` | Probe a live model endpoint once and get a signed latency/availability/consistency verdict vs the provider's claimed SLA. |
| `v1_model_telemetry_rules` | `free` | List model-telemetry verdict rules, the probe procedure, and the auth env-name policy. |
| `v1_subscriptions_rules` | `free` | Machine-readable subscription-status oracle spec: rules, precedence, request schema and verdicts. Free. |
| `v1_subscriptions_status` | ``$0.01`` | Verify an agent-to-agent subscription or session claim: signed active|expired|revoked verdict with the evidence trail. |
| `v1_receivables_factoring_readiness` | ``$0.01`` | Check whether an agent-held receivable is factoring-ready and get a signed ready|not_ready verdict with blocking findings. |
| `v1_receivables_rules` | `free` | List the receivables factoring-readiness rules, check order, and request schema. |

## Per-chain reads & token data (Wave 4, E46-E49)

| `v1_chains_polygon` | `free` | polygon status (chainId 137): verified endpoint kind + head block. chainId-gated, 60s cache. Free. |
| `v1_chains_polygon_gas` | ``$0.01`` | polygon gas snapshot: eth_gasPrice + maxPriorityFee on a chainId-verified keyless RPC. |
| `v1_chains_polygon_rpc` | ``$0.01`` | polygon read-only RPC: allowlisted no-param reads or bounded caller method (eth_blockNumber/eth_chainId/... ). 1MiB cap. |
| `v1_chains_polygon_address` | ``$0.01`` | polygon address snapshot (0x..40hex): balance_wei, nonce, is_contract on a chainId-verified RPC. |
| `v1_chains_polygon_tx` | ``$0.01`` | polygon tx lookup (0x..64hex): eth_getTransactionByHash + receipt; tx_not_found is a valid $0.01 verdict. |
| `v1_chains_arbitrum` | `free` | arbitrum status (chainId 42161): verified endpoint kind + head block. chainId-gated, 60s cache. Free. |
| `v1_chains_arbitrum_gas` | ``$0.01`` | arbitrum gas snapshot: eth_gasPrice + maxPriorityFee on a chainId-verified keyless RPC. |
| `v1_chains_arbitrum_rpc` | ``$0.01`` | arbitrum read-only RPC: allowlisted no-param reads or bounded caller method (eth_blockNumber/eth_chainId/... ). 1MiB cap. |
| `v1_chains_arbitrum_address` | ``$0.01`` | arbitrum address snapshot (0x..40hex): balance_wei, nonce, is_contract on a chainId-verified RPC. |
| `v1_chains_arbitrum_tx` | ``$0.01`` | arbitrum tx lookup (0x..64hex): eth_getTransactionByHash + receipt; tx_not_found is a valid $0.01 verdict. |
| `v1_chains_optimism` | `free` | optimism status (chainId 10): verified endpoint kind + head block. chainId-gated, 60s cache. Free. |
| `v1_chains_optimism_gas` | ``$0.01`` | optimism gas snapshot: eth_gasPrice + maxPriorityFee on a chainId-verified keyless RPC. |
| `v1_chains_optimism_rpc` | ``$0.01`` | optimism read-only RPC: allowlisted no-param reads or bounded caller method (eth_blockNumber/eth_chainId/... ). 1MiB cap. |
| `v1_chains_optimism_address` | ``$0.01`` | optimism address snapshot (0x..40hex): balance_wei, nonce, is_contract on a chainId-verified RPC. |
| `v1_chains_optimism_tx` | ``$0.01`` | optimism tx lookup (0x..64hex): eth_getTransactionByHash + receipt; tx_not_found is a valid $0.01 verdict. |
| `v1_chains_avalanche` | `free` | avalanche status (chainId 43114): verified endpoint kind + head block. chainId-gated, 60s cache. Free. |
| `v1_chains_avalanche_gas` | ``$0.01`` | avalanche gas snapshot: eth_gasPrice + maxPriorityFee on a chainId-verified keyless RPC. |
| `v1_chains_avalanche_rpc` | ``$0.01`` | avalanche read-only RPC: allowlisted no-param reads or bounded caller method (eth_blockNumber/eth_chainId/... ). 1MiB cap. |
| `v1_chains_avalanche_address` | ``$0.01`` | avalanche address snapshot (0x..40hex): balance_wei, nonce, is_contract on a chainId-verified RPC. |
| `v1_chains_avalanche_tx` | ``$0.01`` | avalanche tx lookup (0x..64hex): eth_getTransactionByHash + receipt; tx_not_found is a valid $0.01 verdict. |
| `v1_chains_bnb` | `free` | bnb status (chainId 56): verified endpoint kind + head block. chainId-gated, 60s cache. Free. |
| `v1_chains_bnb_gas` | ``$0.01`` | bnb gas snapshot: eth_gasPrice + maxPriorityFee on a chainId-verified keyless RPC. |
| `v1_chains_bnb_rpc` | ``$0.01`` | bnb read-only RPC: allowlisted no-param reads or bounded caller method (eth_blockNumber/eth_chainId/... ). 1MiB cap. |
| `v1_chains_bnb_address` | ``$0.01`` | bnb address snapshot (0x..40hex): balance_wei, nonce, is_contract on a chainId-verified RPC. |
| `v1_chains_bnb_tx` | ``$0.01`` | bnb tx lookup (0x..64hex): eth_getTransactionByHash + receipt; tx_not_found is a valid $0.01 verdict. |
| `v1_chains_unichain` | `free` | unichain status (chainId 130): verified endpoint kind + head block. chainId-gated, 60s cache. Free. |
| `v1_chains_unichain_gas` | ``$0.01`` | unichain gas snapshot: eth_gasPrice + maxPriorityFee on a chainId-verified keyless RPC. |
| `v1_chains_unichain_rpc` | ``$0.01`` | unichain read-only RPC: allowlisted no-param reads or bounded caller method (eth_blockNumber/eth_chainId/... ). 1MiB cap. |
| `v1_chains_unichain_address` | ``$0.01`` | unichain address snapshot (0x..40hex): balance_wei, nonce, is_contract on a chainId-verified RPC. |
| `v1_chains_unichain_tx` | ``$0.01`` | unichain tx lookup (0x..64hex): eth_getTransactionByHash + receipt; tx_not_found is a valid $0.01 verdict. |
| `v1_chains_worldchain` | `free` | worldchain status (chainId 480): verified endpoint kind + head block. chainId-gated, 60s cache. Free. |
| `v1_chains_worldchain_gas` | ``$0.01`` | worldchain gas snapshot: eth_gasPrice + maxPriorityFee on a chainId-verified keyless RPC. |
| `v1_chains_worldchain_rpc` | ``$0.01`` | worldchain read-only RPC: allowlisted no-param reads or bounded caller method (eth_blockNumber/eth_chainId/... ). 1MiB cap. |
| `v1_chains_worldchain_address` | ``$0.01`` | worldchain address snapshot (0x..40hex): balance_wei, nonce, is_contract on a chainId-verified RPC. |
| `v1_chains_worldchain_tx` | ``$0.01`` | worldchain tx lookup (0x..64hex): eth_getTransactionByHash + receipt; tx_not_found is a valid $0.01 verdict. |
| `v1_chains_reads_rules` | `free` | Chain read rules: alias/chainId table, RPC allowlists, address/hash shapes, verdict semantics. Free. |
| `v1_chains_token_balance` | ``$0.01`` | ERC-20 balanceOf + metadata (symbol/decimals/name) on any supported chain, gate-verified eth_call, exact formatted amount. |
| `v1_chains_token_meta` | ``$0.01`` | ERC-20 metadata on any supported chain: name/symbol/decimals/totalSupply via gate-verified eth_call. |
| `v1_chains_token_rules` | `free` | ERC-20 token-read spec: chains, ABI signatures/selectors, request schema, rules and verdict semantics. Free. |
| `v1_tokens_launch_digest` | ``$0.01`` | New token-pair digest since a timestamp with a signed pre-trade risk verdict per pair (liquidity/freshness). |
| `v1_tokens_launch_rules` | `free` | Machine-readable launch-digest spec: monitored venues, chains, freshness window and the risk-rule table. Free. |
| `v1_stablecoin_reserves` | ``$0.01`` | Signed reserve digest for USDC, USDT, EURC and DAI: latest reserve figures, attestation timestamps and a per-issuer staleness verdict. |
| `v1_stablecoin_reserve_rules` | `free` | Machine-readable stablecoin reserve-digest spec: sources, staleness thresholds and the verdict table. Free. |
