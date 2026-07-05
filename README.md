<!-- mcp-name: io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp -->
# DDG Agent-Payable Services

**Pay-per-call AI agent services gateway.** DDG gives agents one x402/direct-crypto entry point for callable tools, OpenAI-compatible routes, readiness audits, MCP security checks, discovery repair, receipts, and marketplace-ready proof artifacts.

**124 x402/direct-crypto services for AI agents.** The largest agent-payable service surface in the x402 ecosystem — from $0.001 utilities (DNS, hash, UUID) to $0.01 social/financial/agent-infra services. All fully automated with zero human in the loop. Includes an **OpenAI-compatible gateway** (`/v1/chat/completions`, `/v1/models`, `/v1/embeddings`).

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

## Service Catalog (124 services)

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

### Full catalog
See [pricing.json](https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json) for all 124 services.

## Discovery

| Surface | URL |
|---|---|
| AI manifest | `/.well-known/ai` |
| x402 discovery | `/.well-known/x402` |
| OpenAPI spec | `/openapi.json` (128 paths) |
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
