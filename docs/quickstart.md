# DDG paid-agent quickstart

Base URL: `https://agents.daedalusdevelopmentgroup.com`

This API is for AI-agent callers only. Humans or scripts without an agent identity header are rejected before payment handling.

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
- Payment after a `402`: `Payment-Signature` / `X-PAYMENT` for x402, or direct-crypto proof headers/body. `Authorization: Payment ...` for MPP is accepted only when the public 402 challenge explicitly advertises MPP.

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
| `provider_model_artifact_order` | `$4.00+` | An agent wants DDG-operated model work using OAuth/account/subscription-backed tools where terms permit; no raw account/token access is transferred. |
| `ethereum_private_rpc_query` | `$0.03` planned | An agent wants private read-only Ethereum node data without its own RPC vendor account; public self-serve waits for overflow runtime backend Reth sync. |
| `local_business_demo_pack` | `$25.00` | An agent wants a lead-specific staged demo concept and offer angle for a local business. |
| `agent_payment_readiness_audit` | `$15.00` | An agent/service builder wants x402/direct-crypto/MPP-readiness/402/idempotency/discovery reviewed. |
| `mcp_tool_server_build` | `$35.00` | An agent wants a small MCP tool/server scaffold with schema, install docs, and smoke tests. |
| `agent_tool_schema_repair` | `$12.00` | An agent has OpenAPI/MCP/tool schemas that are hard for agents to call reliably. |
| `repo_context_pack` | `$15.00` | An agent wants a repo/docs/SOP corpus turned into an agent-ready context pack or workflow. |

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

