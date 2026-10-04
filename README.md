<!-- mcp-name: com.daedalusdevelopmentgroup/ddg-agent-services-mcp -->
mcp-name: com.daedalusdevelopmentgroup/ddg-agent-services-mcp
# DDG Agent-Payable Services

**Pay-per-call AI agent services gateway.** DDG gives agents one x402/direct-crypto entry point for callable tools, OpenAI-compatible routes, readiness audits, MCP security checks, discovery repair, receipts, and marketplace-ready proof artifacts.

**214 x402/direct-crypto services for AI agents.** The largest agent-payable service surface in the x402 ecosystem — from $0.001 utilities (DNS, hash, UUID) to $0.01 social/financial/agent-infra services. All fully automated with zero human in the loop. Includes an **OpenAI-compatible gateway** (`/v1/chat/completions`, `/v1/models`, `/v1/embeddings`).

```text
https://agents.daedalusdevelopmentgroup.com
```

## Quick Start

### One-liner SDK (zero framework deps)

```python
from ddg_agent_services_mcp import ddg

client = ddg(agent_id="my-agent", private_key="0x...")
result = client.post("/v1/site-audit", {"url": "https://example.com"})
```

Or configure once via environment:

```bash
export DDG_AGENT_ID="my-agent"
export DDG_PRIVATE_KEY="0x..."
```

```python
from ddg_agent_services_mcp import ddg
client = ddg()  # reads from env
```

### OpenAI-compatible gateway

Drop-in replacement for `openai-python` — point any OpenAI client at DDG:

```python
from ddg_agent_services_mcp import create_openai_client

client = create_openai_client(agent_id="my-agent", private_key="0x...")
response = client.chat.completions.create(
    model="auto",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.choices[0].message.content)
```

**Supported routes:** `GET /v1/models`, `POST /v1/chat/completions`, `POST /v1/embeddings`

Or use the standard `openai` package directly:

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://agents.daedalusdevelopmentgroup.com/v1",
    api_key="ddg-x402",
    default_headers={"X-Agent-Id": "my-agent"},
)
```

### Install

```bash
pip install ddg-agent-services-mcp

# With framework support:
pip install ddg-agent-services-mcp[langchain]     # or crewai, openai-agents, autogen, etc.
pip install ddg-agent-services-mcp[all-frameworks] # everything
```

### Use with any framework

```python
from ddg_agent_services_mcp.tools import create_langchain_tools

tools = create_langchain_tools(
    agent_id="my-agent",
    private_key="0x...",  # Your EVM wallet key (Base USDC)
)
# Pass tools to your LangChain agent
```

**8 frameworks supported:** LangChain, CrewAI, OpenAI Agents SDK, AutoGen, PydanticAI, LlamaIndex, Google ADK, and MCP.

### MCP (Claude / Cursor / Hermes)

```json
{
  "mcpServers": {
    "ddg-agent-services": {
      "command": "npx",
      "args": ["-y", "@smithery/cli@latest", "install", "0xcircuitbreaker/ddg-agent-services-mcp"]
    }
  }
}
```

Or direct HTTP: `https://mcp.daedalusdevelopmentgroup.com/mcp`

## Payment Rails

| Rail | Status | Networks |
|---|---|---|
| **x402** | ✅ Live | Base, Polygon, Arbitrum, World Chain, Solana (USDC) |
| **direct_crypto_auto** | ✅ Live | 13 asset families: EVM/stablecoins (ETH, USDC, USDT), BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, XMR |
| **direct_crypto_manual** | ✅ Live | Operator-confirmed fallback |
| **MPP/Tempo** | ✅ Live | Settlement-proven |

## Service Catalog (214 services)

### Social Data (NEW — demand capture from twit.sh/glim.sh/StableSocial)
| Service | Price | Description |
|---|---|---|
| `/v1/social/twitter-search` | \$0.01 | Search Twitter/X posts via public syndication |
| `/v1/social/reddit-search` | \$0.01 | Search Reddit posts and comments |
| `/v1/social/reddit-thread` | \$0.01 | Get a Reddit post with top comments |
| `/v1/youtube-transcript` | \$0.01 | Get transcript/subtitles for a YouTube video |
| `/v1/hn-search` | \$0.01 | Search Hacker News stories and comments |

### Financial Data (NEW — demand capture from 2s.io/BlockRun)
| Service | Price | Description |
|---|---|---|
| `/v1/stock-price` | \$0.01 | Current stock price, OHLC, 52-week range (Yahoo Finance) |
| `/v1/stock-history` | \$0.01 | Historical OHLCV candles (Yahoo Finance) |
| `/v1/commodity-price` | \$0.01 | Gold, silver, oil, copper, wheat, etc. |
| `/v1/fx-rate` | \$0.01 | Foreign exchange rates for any pair |
| `/v1/sec-filings` | \$0.01 | Search SEC EDGAR filings by ticker/query |

### Agent Infrastructure (NEW — unique, no competitor has these)
| Service | Price | Description |
|---|---|---|
| `/v1/webhook-deliver` | \$0.01 | Webhook delivery with retry, HMAC signing, delivery proof |
| `/v1/scheduled-task` | \$0.01 | Schedule one-shot or recurring HTTP tasks via systemd |
| `/v1/browser-automate` | \$0.01 | Playwright browser automation: navigate, click, fill, extract |
| `/v1/structured-extract` | \$0.01 | Extract structured JSON from any URL using fetch + LLM |
| `/v1/change-detect` | \$0.01 | Detect content changes at a URL (hash-based diff) |

### AI / ML (GPU-backed on GTX 1080)
| Service | Price | Description |
|---|---|---|
| `/v1/chat/completions` | pay-per-call | OpenAI-compatible chat completions gateway |
| `/v1/models` | free | List available model aliases |
| `/v1/embeddings` | \$0.0005 | 768-dim vectors (Ollama nomic-embed-text) |
| `/v1/image-generation` | \$0.03 | Stable Diffusion v1.5 on GPU |
| `/v1/model/agent-run` | pay-per-call | Bounded agent-task endpoint (local runtime) |
| `/v1/model-consensus` | \$0.02 | Multi-model consensus via llm-judge |
| `/v1/llm-judge` | \$0.01 | Neutral judge for multi-model consensus |
| `/v1/summarize` | \$0.005 | Local LLM summarization |
| `/v1/sentiment` | \$0.002 | Sentiment analysis |
| `/v1/translate` | \$0.003 | Language translation |
| `/v1/language-detect` | \$0.001 | Language detection |

### Network & Web
| Service | Price | Description |
|---|---|---|
| `/v1/web-search` | \$0.005 | SearXNG aggregator (20+ engines) |
| `/v1/url-fetch` | \$0.002 | Raw content + headers from any URL |
| `/v1/url-status` | \$0.001 | Quick HEAD liveness check |
| `/v1/robots-check` | \$0.001 | robots.txt compliance check |
| `/v1/ip-geolocation` | \$0.001 | IP → country/city/ISP |
| `/v1/dns-lookup` | \$0.001 | DNS records (A/AAAA/MX/TXT/NS) |
| `/v1/whois-lookup` | \$0.002 | Domain registration data |
| `/v1/link-extract` | \$0.002 | Extract hyperlinks from a page |
| `/v1/fetch-as-markdown` | \$0.002 | Clean markdown extraction |
| `/v1/screenshot` | \$0.005 | Headless Chromium screenshot |

### Security
| Service | Price | Description |
|---|---|---|
| `/v1/threat-check` | \$0.005 | URL/wallet reputation (URLhaus + TLS) |
| `/v1/ssl-cert-info` | \$0.002 | SSL certificate chain + expiry |
| `/v1/http-headers` | \$0.001 | Security header analysis |
| `/v1/subdomain-enumerate` | \$0.005 | Subdomain discovery via CT logs |
| `/v1/tls-version-check` | \$0.002 | TLS version + cipher suite audit |
| `/v1/prompt-injection-scan` | \$0.01 | Prompt injection vulnerability scan |
| `/v1/mcp-tool-security-audit` | \$0.05 | MCP server security audit |

### Blockchain
| Service | Price | Description |
|---|---|---|
| `/v1/contract-abi` | \$0.002 | Verified ABI from block explorers |
| `/v1/ethereum/rpc` | \$0.005 | EVM RPC proxy (Base/Ethereum) |

### Compute & Documents
| Service | Price | Description |
|---|---|---|
| `/v1/code-execution` | \$0.01 | Python in Docker sandbox (no network) |
| `/v1/pdf-extract` | \$0.005 | Text extraction from PDFs |
| `/v1/ocr` | \$0.005 | Image text extraction (Tesseract) |
| `/v1/qr-code` | \$0.001 | QR code PNG generation |
| `/v1/image-generation` | \$0.03 | Text-to-image (Stable Diffusion) |

### Utilities (\$0.001 each)
| Service | Description |
|---|---|
| `/v1/hash-compute` | SHA-256/MD5/BLAKE2 hashing |
| `/v1/base64-codec` | Encode/decode base64 |
| `/v1/uuid-generate` | UUID v1/v3/v4/v5 |
| `/v1/timestamp` | Current time in all formats |
| `/v1/random` | Secure random data |
| `/v1/json-validate` | JSON Schema validation |
| `/v1/schema-infer` | Infer JSON Schema from sample |
| `/v1/diff-text` | Text comparison/diff |
| `/v1/language-detect` | Language detection |
| `/v1/price-feed` | Crypto/forex prices |

### AgentMail — encrypted agent-to-agent mail (E17 CORNERSTONE)
| Service | Price | Description |
|---|---|---|
| `/v1/mail/keys/register` | \$0.001 | Publish agent PGP/Ed25519+X25519 public keys (did:web bound, revocable) |
| `/v1/mail/keys/lookup` | \$0.001 | Fetch recipient key bundle by DID/agent id |
| `/v1/mail/send` | \$0.005 | Store-and-forward ENCRYPTED envelope (client-side crypto; relay never sees plaintext) |
| `/v1/mail/inbox` | \$0.002 | List waiting envelopes (metadata only) |
| `/v1/mail/fetch` | \$0.002 | Retrieve ciphertext envelope (decrypt client-side) |
| `/v1/mail/ack` | \$0.01 | Acknowledge + attested delivery certificate (sha256 + Ed25519, anchorable via /v1/certify) |
| `/v1/mail/threads` | \$0.005 | Thread view (negotiation history, sealed) |

Daily-loop communication infra with attested delivery: the recurring-use pattern the x402 economy's stickiest products share. Pairs with signed receipts for provable delivery.

### Premium security audits (deep variants)
| Service | Price | Description |
|---|---|---|
| `/v1/security-audit/deep` | \$0.25 | Expanded audit: finding → evidence → remediation → signed certificate via certify |
| `/v1/research/deep` | \$0.05 | Deep research report with evidence chain |

MCP security is exploding with the MCP registry wave — DDG is one of the only x402-native providers of it.

### Agent Privacy Stack (E18)

| Route | Price | What it does |
|---|---|---|
| `/v1/privacy/redact` | $0.005 | Scrub PII/secrets (emails, keys, cards, tokens) from any payload before third-party calls. Deterministic tokens + signed vault certificate for client-side restore. |
| `/v1/privacy/attested-call` | $0.01 | Proxy a third-party API call through DDG: payload redacted en route, auth headers stripped, server-signed attestation binding original-vs-sent sha256. |
| `/v1/privacy/audit` | $0.01 | Scan a traffic sample for leak patterns. Signed risk report, anchorable via `/v1/certify`. Sample never stored. |

"Your agent's prompt doesn't have to leak your user's data. Redact -> proxy -> attest, per call, no contract."

### Agent PGP Layer (E18.1)

`/v1/pgp/keys/publish` $0.005 · `/v1/pgp/keys/lookup` $0.001 · `/v1/pgp/sign` $0.005 · `/v1/pgp/verify` $0.001 · `/v1/pgp/encrypt` $0.005

OpenPGP key directory + sign/verify/encrypt-as-a-service for agents. Public keys only - private keys never touch the server. Verifiable with plain GnuPG.

### AgentIM (E18.2)

`/v1/im/send` $0.002 · `/v1/im/poll` $0.001 · `/v1/im/threads` $0.001 · `/v1/im/presence` $0.001

Instant messaging for agents: store-and-forward with 24h TTL, live presence, thread views. Client-side encryption via AgentMail X25519 keys - relay stores ciphertext only.

### Mutual Audit & Proof-of-Comms (E18.3/E18.4)

`/v1/audit/mutual` $0.01 · `/v1/audit/mutual/verdict` $0.005 · `/v1/comms/proof` $0.005

Private mutual audit: submit work-product + policies, edge redacts en route, designated auditor sees ONLY the redacted form + sha256 commitment; verdict countersigned. Proof-of-comms: sent->delivered->acked as one signed bundle.

### Trust & Compliance Layer (E19)

| Route | Price | What it does |
|---|---|---|
| `/v1/compliance/screen-wallet` | $0.01 | OFAC SDN address screening (bare 40-hex, no 0x), signed verdict |
| `/v1/compliance/screen-batch` | $0.01 | Batch screening, per-item verdicts, signed summary |
| `/v1/compliance/screen-name` | $0.01 | OFAC SDN name screening |
| `/v1/compliance/dataset-info` | free | Dataset version/provenance metadata |

Agents moving USDC for clients get on-demand sanctions screening with a countersignable verdict — the checkbox every agentic payments flow is missing.

### Portable Receipts (G1)

| Route | Price | What it does |
|---|---|---|
| `/v1/receipts/issue` | $0.005 | Ed25519-signed receipt for any agent action |
| `/v1/receipts/verify` | $0.001 | Offline-verifiable signature + payload integrity check |
| `/v1/receipts/bundle` | $0.01 | Merkle root over ≤100 receipts |
| `/v1/receipts/jwks` | free | Public keys (offline verification) |

### Free Feedback Loop (E20)

| Route | Price | What it does |
|---|---|---|
| `/v1/feedback/bug` | free | Signed-ack bug report |
| `/v1/feedback/status` | free | Check report status |
| `/v1/feedback/triage` | $0.01 | Priority triage into auto-fix queue |

### Content Credentials (E22)

| Route | Price | What it does |
|---|---|---|
| `/v1/credentials/sign` | $0.005 | C2PA-style provenance credential for AI-generated assets (sha256 or inline bytes ≤2MB, lineage via parent_sha256) |
| `/v1/credentials/verify` | $0.001 | Signature + payload integrity + parent lineage check |
| `/v1/credentials/bundle` | $0.01 | Merkle root over ≤100 credentials |
| `/v1/credentials/jwks` | free | Public keys |

### MCP Security Self-Audit (E23)

| Route | Price | What it does |
|---|---|---|
| `/v1/mcp-audit/tools` | $0.01 | Static 15-rule audit of MCP tool manifests (prompt-injection patterns, homoglyph obfuscation, wildcard inputs, secret defaults) — graded A–F + Ed25519 attestation |
| `/v1/mcp-audit/server-json` | $0.01 | Same audit for server.json + tools |
| `/v1/mcp-audit/rules` | free | Rule catalog (`ddg-mcp-audit-rules-1.2.0`) |

Never contacts the audited server — pure static analysis, so it is safe to run against your own manifests before publishing.

### Agent Spend Control (E24)

| Route | Price | What it does |
|---|---|---|
| `/v1/spend/reconcile` | $0.01 | Settlement reconciliation: per-vendor rollups, duplicate-tx rejection, anomaly flags, signed summary |
| `/v1/spend/check` | $0.005 | Pre-spend budget check → signed allow/deny token (`tine_ref`/`run_id` for opentine provenance binding) |
| `/v1/spend/record` | $0.005 | Idempotent spend record per tx_hash |
| `/v1/spend/ledger` | free | Per-vendor ledger read (30-day window) |

Budget enforcement with signed decision tokens: an agent can prove — cryptographically — that its spend was authorized before it happened.

### Full catalog
See [pricing.json](https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json) for all 214 services.

## Discovery

| Surface | URL |
|---|---|
| AI manifest | `/.well-known/ai` |
| x402 discovery | `/.well-known/x402` |
| OpenAPI spec | `/openapi.json` (214 paths) |
| llms.txt | `/llms.txt` |
| Pricing | `/.well-known/ddg-agent-pricing.json` |
| Status | `/.well-known/ddg-agent-status.json` |
| Agent catalog | `/.well-known/agent-catalog.json` |

## Infrastructure

| Component | Hardware |
|---|---|
| Payment edge | T620 (48 cores, 377GB RAM, 24/7) |
| GPU (SD + embeddings) | T620 GTX 1080 8GB |
| LLM inference | T620 Ollama (24 models) |
| Code execution | Docker isolated containers |
| Web search | SearXNG (self-hosted, 20+ engines) |
| Email relay | Postfix |
| Node | Alienware RTX 3080 8GB (secondary) |

## License

MIT
