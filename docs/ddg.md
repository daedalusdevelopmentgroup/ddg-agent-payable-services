# DDG Agent-Payable Services — ddg.md

> The everything-endpoint for AI agents: **90+ pay-per-call tools + an OpenAI-compatible LLM gateway, behind one USDC wallet.** No API keys, no accounts, no monthly minimums. Pay per call via **x402** (USDC on Base). Most calls cost pennies; price capped at **$0.10/call**.

Base URL: `https://agents.daedalusdevelopmentgroup.com`

## Why
Your agent can't sign up for 90 SaaS accounts or enter a credit card — it can only sign a transaction. DDG gives it 90+ tools + every major LLM behind a single wallet. The agent economy isn't bottlenecked on intelligence; it's bottlenecked on billing. x402 fixes that.

## Integrate in one line (pick your stack)

**OpenAI SDK (any language)** — point `base_url` at DDG:
```python
client = OpenAI(base_url="https://agents.daedalusdevelopmentgroup.com/v1")
# GET /v1/models is free; POST /v1/chat/completions is metered (from $0.0002/call) and
# returns 402 until an x402 payment header is attached (the clients below do that automatically).
```

**Python** — auto-pays x402:
```bash
pip install "ddg-agent-services-mcp[openai]"
```
```python
from ddg_agent_services_mcp import ddg, create_openai_client
ddg(agent_id="me", private_key="0x"+"1"*64).get("/v1/model-catalog")   # free
create_openai_client(agent_id="me", private_key="0x<funded base key>").chat.completions.create(
    model="glm-4.5-air", messages=[{"role":"user","content":"hi"}])
```

**MCP (Claude Code / Cursor / Cline)** — remote, no install:
`https://mcp.daedalusdevelopmentgroup.com/mcp` · Registry: `io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp`

**Local x402-paying proxy** — make DDG any runtime's provider:
```bash
pip install ddg-router && ddg-router &      # OpenAI-compatible proxy on 127.0.0.1:4020, auto-pays x402
```

**One installer for your whole runtime** (native for OpenClaw/Hermes, MCP for Claude Code/OpenCode/Codex/Kimi):
```bash
pip install ddg-connect && ddg-connect install --target all
```

## What's available (90+ tools)
- **LLM gateway** — OpenAI-compatible `/v1/chat/completions`, `/v1/models`, `/v1/embeddings`; many models, metered from **$0.0002/call**, no cap.
- **Blockchain** — free-tier Ethereum RPC (`/v1/ethereum/rpc`, 100 free/agent/24h), contract-abi, prediction-markets (Polymarket), dex-pairs (DexScreener).
- **Market data** — stock price/history, fx-rate, commodity-price, hn-search, sec-filings.
- **Web/utilities** — web-search, DNS/WHOIS, hash, QR, OCR, PDF extract, screenshots, embeddings, translate, summarize, structured-extract, change-detect, browser-automate, webhook-deliver, scheduled-task.
- **Security/audit suite** — mcp-tool-security-audit, prompt-injection-scan, npm/python dependency-risk-scan, secret-leak-scan, production-security-audit, agent-checkout-conformance-audit.
- **Provenance (.tine/opentine)** — verify/diff/provenance-chain.

Live catalog + prices: `GET /v1/model-catalog` (models) · `GET /.well-known/ddg-agent-pricing.json` (all routes) · `GET /openapi.json`.

## The x402 pay flow (what the clients automate)
1. Call an endpoint → `402 Payment Required` with an x402 v2 challenge (Base USDC, amount, payTo).
2. Sign an EIP-3009 USDC authorization for that amount with your Base wallet.
3. Retry with the signed `PAYMENT-SIGNATURE` header → `200` + result + receipt.
Most routes grant **free-trial calls per agent** (send `X-Agent-Id`, no wallet needed to start).

## DDG vs the field
| | **DDG** | BlockRun | OpenRouter | StableEnrich |
|---|---|---|---|---|
| Sells | 90+ tools **+** LLM gateway | LLMs + some data | LLM routing | data reselling |
| Pay | x402 / USDC on Base, no key | x402 / USDC | API key + prepay | x402 |
| LLM pricing | from **$0.0002**/call, OpenAI-compatible | cost + 5% | provider + markup | — |
| Non-LLM tools | **90+** (RPC, data, security audits, automation) | limited | none | data only |
| Price cap | **$0.10/call** | none | none | none |
| Free trial | **per agent, per route** | none | none | none |
| MCP server | ✅ (Official Registry) | ✅ | — | — |
| Security/audit tools | ✅ (unique) | — | — | — |

**Positioning:** if OpenRouter is the *model* layer, DDG is the *capability* layer — every major model **and** 90+ tools, one wallet, pay-per-call.

## Discovery
`/.well-known/x402` · `/openapi.json` · `/.well-known/ddg-agent-pricing.json` · `/llms.txt` · `/AGENTS.md` · MCP Registry `io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp` · PyPI `ddg-agent-services-mcp`.
