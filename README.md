<!-- mcp-name: com.daedalusdevelopmentgroup/ddg-agent-services-mcp -->
mcp-name: com.daedalusdevelopmentgroup/ddg-agent-services-mcp
# DDG Agent-Payable Services

**Pay-per-call AI agent services gateway.** DDG gives agents one x402/direct-crypto entry point for callable tools, OpenAI-compatible routes, readiness audits, MCP security checks, discovery repair, receipts, and marketplace-ready proof artifacts.

**214 x402/direct-crypto services for AI agents.** The largest agent-payable service surface in the x402 ecosystem — from $0.01 utilities (DNS, hash, UUID) to $0.01 social/financial/agent-infra services. All fully automated with zero human in the loop. Includes an **OpenAI-compatible gateway** (`/v1/chat/completions`, `/v1/models`, `/v1/embeddings`).

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

## Service Catalog (328 services)

### Trust & Identity Verification (wave 5)
| Route | Price | Description |
|---|---|---|
| `/v1/auth/jwt-verify` | \$0.01 | Verify JWT/JWS against issuer JWKS: alg allowlist (no none/symmetric), exp/nbf/aud/iss, kid rotation, SSRF-guarded fetch |
| `/v1/identity/did-resolve` | \$0.01 | did:web fetch+validate, did:key decode (ed25519/secp256k1), extracted verification keys |
| `/v1/identity/vc-verify` | \$0.01 | VerifiableCredential verify: JWT-VC (full sig) or JSON-LD (structural + proof when payload supplied) |
| `/v1/compliance/breach-check` | \$0.01 | HIBP k-anonymity password breach check — only 5 hash chars leave the caller |
| `/v1/trust/verify-jwks` | free | Public Ed25519 key for offline verification of trust-lane verdicts |

### Agent RAG & Content Ops (wave 5)
| Route | Price | Description |
|---|---|---|
| `/v1/rag/index` | \$0.01 | Named persisted corpus: BM25 + nomic-embed-text embeddings |
| `/v1/rag/search` | \$0.01 | Hybrid retrieval with tunable weight |
| `/v1/rag/answer` | \$0.01 | Cited answer generation (qwen2.5:7b) grounded in your corpus |
| `/v1/rag/status` | free | Corpus list + model availability |
| `/v1/content/extract` | \$0.01 | Text from PDF/DOCX/TXT/MD (base64 in) |
| `/v1/content/chunk` | \$0.01 | Size/overlap chunking with per-chunk hashes |
| `/v1/content/search` | \$0.01 | Stateless BM25 over request-supplied docs |
| `/v1/content/toolkit` | free | Parser/model/limit manifest |

### C2PA for Audio/Video (wave 5, E22 extension)
| Route | Price | Description |
|---|---|---|
| `/v1/c2pa/sign-av` | \$0.01 | Signed credential for audio/video: segment-hash Merkle root, Ed25519 trust root |
| `/v1/c2pa/verify-av` | \$0.01 | Signature + rebind + segment-root + duration checks |
| `/v1/c2pa/av-info` | \$0.01 | Pure-Python container fingerprint (mp4/mp3/ogg/wav/flac/webm) + segment hashes |

### Network & Deliverability Intelligence (wave 5)
| Route | Price | Description |
|---|---|---|
| `/v1/email/preflight` | \$0.01 | DNS-only deliverability: MX + RFC-subset SPF (with sender-IP eval) + DMARC + DKIM probe + rDNS. Never sends mail. |
| `/v1/email/mx-route` | \$0.01 | Ordered MX precedence chain → A/AAAA endpoints (null-MX aware) |
| `/v1/moderation/scan` | \$0.01 | Offline deterministic moderation: profanity, PII (SSN/Luhn/cards), wallets, jailbreak patterns |
| `/v1/infra/security-posture` | \$0.01 | SSRF-guarded fetch + TLS summary + security-header grading |
| `/v1/infra/tls-verify` | \$0.01 | Leaf cert forensics: expiry, SANs, key type, self-signed, sig algorithm |
| `/v1/infra/ports` | \$0.01 | Bounded TCP sweep (≤16 ports, no banner probing) |
| `/v1/net/dns-lookup` | \$0.01 | 10 record types + optional validated public resolver override |
| `/v1/net/http-probe` | \$0.01 | Probe with timing, body sha256, per-hop redirect chain |
| `/v1/net/url-lint` | \$0.01 | Offline URL parse/normalize + issue list |
| `/v1/intel/domain-reputation` | \$0.01 | DNS intel + Spamhaus/SORBS RBL + quick TLS, scored 0-100 |
| `/v1/intel/url-reputation` | \$0.01 | RBL + SURBL + shortener/phishing heuristics → safe/suspicious/block |
| `/v1/netops/status` | free | Live dependency status page for the intel lane |

### Threat Intel, IaC Guard & Moderation LLM (wave 5b)
| Route | Price | Description |
|---|---|---|
| `/v1/intel/fusion` | \$0.01 | Confidence-weighted fusion of up to 25 indicators (domain/ip/url/hash/email) + external source labels into one signed verdict |
| `/v1/intel/tech-fingerprint` | \$0.01 | Web stack fingerprint (CMS/framework/server/CDN) from headers+HTML+cookies, or SSRF-guarded bounded fetch |
| `/v1/iac/guard` | \$0.01 | Static IaC scan (Terraform/CloudFormation/K8s/Dockerfile): secrets, wildcard IAM, open ingress, privileged containers, :latest |
| `/v1/intel/redos-scan` | \$0.01 | Structural ReDoS risk analysis of up to 25 regexes (compiles, never matches — analyzer immune) |
| `/v1/moderation/llm-scan` | \$0.01 | Semantic moderation via local LLM with deterministic heuristic fallback; companion to `/v1/moderation/scan` |

Note: `/v1/intel/fusion` + `/v1/intel/url-reputation` + `/v1/intel/domain-reputation` compose into a full threat-intel desk. Hash-level verdicts fuse via `fusion` (bring labels from any feed).

### Payment forensics, MCP conformance, runtime postmortem & archive preflight (wave 6)
| Route | Price | Description |
|---|---|---|
| `/v1/payments/retry-advice` | \$0.01 | Signed safe-to-retry / double-spend-risk verdict for failed x402 payments (CDP facilitator reason-code ruleset, optional Base nonce read) |
| `/v1/x402/explain` | \$0.01 | Plain-English root cause + failing rule + fix for any failed x402/402 payment response |
| `/v1/mcp/conformance` | \$0.01 | Live MCP spec-conformance probe: real JSON-RPC handshake, wire-revision detection (2025-11-25 vs 2026-07-28), graded checks, signed verdict |
| `/v1/mcp/conformance/spec-versions` | free | Supported MCP spec revisions + conformance check catalog |
| `/v1/runtime/postmortem` | \$0.01 | Agent trace failure diagnosis: loop/truncation/cascade/hallucinated-tool detection + prose diagnosis (local LLM), signed |
| `/v1/runtime/cluster` | \$0.01 | 10–200 traces -> failure-mode clustering + dominant root-cause distribution, signed |
| `/v1/file/archive-preflight` | \$0.01 | zip-slip + zip-bomb structure scan of untrusted archives (metadata only, no extraction), signed |
| `/v1/web/wayback-lookup` | \$0.01 | Internet Archive CDX lookup: was this URL archived, closest snapshot (1–50 urls) |
| `/v1/web/wayback-report` | \$0.01 | Batch link-rot report (1–500 urls): coverage %, per-url status, signed |

### EU e-invoice, image C2PA, SEPA MVR, comms guard (wave 7)
| Route | Price | Description |
|---|---|---|
| `/v1/validate-ubl` | \$0.01 | UBL 2.1 e-invoice validation: XSD vs cached OASIS schema, EN 16931 structural rules, VAT math. Signed verdict |
| `/v1/validate-cii` | \$0.01 | Cross-Industry Invoice (EN 16931 binding) structural subset validation |
| `/v1/einvoice/specs` | free | Supported profiles + cached standards (versions, sha256) |
| `/v1/c2pa/sign-image` | \$0.01 | Embed signed DDG content credential into PNG/JPEG/WebP (PNG tEXt, JPEG APP1, sidecar) |
| `/v1/c2pa/verify-image` | \$0.01 | Verify image credential: signature + pixel-hash + claim intactness. Signed verdict |
| `/v1/c2pa/image-info` | \$0.01 | Format sniff, dimensions, chunk map, has-credential probe |
| `/v1/payment/mvr` | \$0.01 | SEPA ISO 20022 business rules (pain.001/pain.008): IBAN mod-97, control sums, EPC MVR rejects |
| `/v1/payment/mvr/rules` | free | SEPA MVR rule catalog |
| `/v1/email/scam-screen` | \$0.01 | Received-mail BEC/scam screen: reply-to mismatch, homoglyphs, cousin domains, BEC language. Signed verdict |
| `/v1/email/scam-batch` | \$0.01 | Scam-screen up to 50 emails, per-message + summary |
| `/v1/lint-webhook` | \$0.01 | Webhook replay-safety linter: signature preset, timestamp tolerance, idempotency, dedupe |
| `/v1/lint-webhook/provider-checks` | free | Provider webhook signature presets (stripe/github/shopify/ucp/generic) |

### Compliance composed (wave 5)
| Route | Price | Description |
|---|---|---|
| `/v1/compliance/token-screen` | \$0.01 | Signed pre-trade token passport: GoPlus heuristics + E19 OFAC screen of deployer/owner — the only x402 rug-check with sanctions composition and a countersignable verdict |

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
| `/v1/image-generation` | \$0.01 | Stable Diffusion v1.5 on GPU |
| `/v1/model/agent-run` | pay-per-call | Bounded agent-task endpoint (local runtime) |
| `/v1/model-consensus` | \$0.01 | Multi-model consensus via llm-judge |
| `/v1/llm-judge` | \$0.01 | Neutral judge for multi-model consensus |
| `/v1/summarize` | \$0.01 | Local LLM summarization |
| `/v1/sentiment` | \$0.01 | Sentiment analysis |
| `/v1/translate` | \$0.01 | Language translation |
| `/v1/language-detect` | \$0.01 | Language detection |

### Network & Web
| Service | Price | Description |
|---|---|---|
| `/v1/web-search` | \$0.01 | SearXNG aggregator (20+ engines) |
| `/v1/url-fetch` | \$0.01 | Raw content + headers from any URL |
| `/v1/url-status` | \$0.01 | Quick HEAD liveness check |
| `/v1/robots-check` | \$0.01 | robots.txt compliance check |
| `/v1/ip-geolocation` | \$0.01 | IP → country/city/ISP |
| `/v1/dns-lookup` | \$0.01 | DNS records (A/AAAA/MX/TXT/NS) |
| `/v1/whois-lookup` | \$0.01 | Domain registration data |
| `/v1/link-extract` | \$0.01 | Extract hyperlinks from a page |
| `/v1/fetch-as-markdown` | \$0.01 | Clean markdown extraction |
| `/v1/screenshot` | \$0.01 | Headless Chromium screenshot |

### Security
| Service | Price | Description |
|---|---|---|
| `/v1/threat-check` | \$0.01 | URL/wallet reputation (URLhaus + TLS) |
| `/v1/ssl-cert-info` | \$0.01 | SSL certificate chain + expiry |
| `/v1/http-headers` | \$0.01 | Security header analysis |
| `/v1/subdomain-enumerate` | \$0.01 | Subdomain discovery via CT logs |
| `/v1/tls-version-check` | \$0.01 | TLS version + cipher suite audit |
| `/v1/prompt-injection-scan` | \$0.01 | Prompt injection vulnerability scan |
| `/v1/mcp-tool-security-audit` | \$0.01 | MCP server security audit |

### Blockchain
| Service | Price | Description |
|---|---|---|
| `/v1/contract-abi` | \$0.01 | Verified ABI from block explorers |
| `/v1/ethereum/rpc` | \$0.01 | EVM RPC proxy (Base/Ethereum) |

### Compute & Documents
| Service | Price | Description |
|---|---|---|
| `/v1/code-execution` | \$0.01 | Python in Docker sandbox (no network) |
| `/v1/pdf-extract` | \$0.01 | Text extraction from PDFs |
| `/v1/ocr` | \$0.01 | Image text extraction (Tesseract) |
| `/v1/qr-code` | \$0.01 | QR code PNG generation |
| `/v1/image-generation` | \$0.01 | Text-to-image (Stable Diffusion) |

### Utilities (\$0.01 each)
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
| `/v1/mail/keys/register` | \$0.01 | Publish agent PGP/Ed25519+X25519 public keys (did:web bound, revocable) |
| `/v1/mail/keys/lookup` | \$0.01 | Fetch recipient key bundle by DID/agent id |
| `/v1/mail/send` | \$0.01 | Store-and-forward ENCRYPTED envelope (client-side crypto; relay never sees plaintext) |
| `/v1/mail/inbox` | \$0.01 | List waiting envelopes (metadata only) |
| `/v1/mail/fetch` | \$0.01 | Retrieve ciphertext envelope (decrypt client-side) |
| `/v1/mail/ack` | \$0.01 | Acknowledge + attested delivery certificate (sha256 + Ed25519, anchorable via /v1/certify) |
| `/v1/mail/threads` | \$0.01 | Thread view (negotiation history, sealed) |

Daily-loop communication infra with attested delivery: the recurring-use pattern the x402 economy's stickiest products share. Pairs with signed receipts for provable delivery.

### Premium security audits (deep variants)
| Service | Price | Description |
|---|---|---|
| `/v1/security-audit/deep` | \$0.01 | Expanded audit: finding → evidence → remediation → signed certificate via certify |
| `/v1/research/deep` | \$0.01 | Deep research report with evidence chain |

MCP security is exploding with the MCP registry wave — DDG is one of the only x402-native providers of it.

### Agent Privacy Stack (E18)

| Route | Price | What it does |
|---|---|---|
| `/v1/privacy/redact` | $0.01 | Scrub PII/secrets (emails, keys, cards, tokens) from any payload before third-party calls. Deterministic tokens + signed vault certificate for client-side restore. |
| `/v1/privacy/attested-call` | $0.01 | Proxy a third-party API call through DDG: payload redacted en route, auth headers stripped, server-signed attestation binding original-vs-sent sha256. |
| `/v1/privacy/audit` | $0.01 | Scan a traffic sample for leak patterns. Signed risk report, anchorable via `/v1/certify`. Sample never stored. |

"Your agent's prompt doesn't have to leak your user's data. Redact -> proxy -> attest, per call, no contract."

### Agent PGP Layer (E18.1)

`/v1/pgp/keys/publish` $0.01 · `/v1/pgp/keys/lookup` $0.01 · `/v1/pgp/sign` $0.01 · `/v1/pgp/verify` $0.01 · `/v1/pgp/encrypt` $0.01

OpenPGP key directory + sign/verify/encrypt-as-a-service for agents. Public keys only - private keys never touch the server. Verifiable with plain GnuPG.

### AgentIM (E18.2)

`/v1/im/send` $0.01 · `/v1/im/poll` $0.01 · `/v1/im/threads` $0.01 · `/v1/im/presence` $0.01

Instant messaging for agents: store-and-forward with 24h TTL, live presence, thread views. Client-side encryption via AgentMail X25519 keys - relay stores ciphertext only.

### Mutual Audit & Proof-of-Comms (E18.3/E18.4)

`/v1/audit/mutual` $0.01 · `/v1/audit/mutual/verdict` $0.01 · `/v1/comms/proof` $0.01

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
| `/v1/receipts/issue` | $0.01 | Ed25519-signed receipt for any agent action |
| `/v1/receipts/verify` | $0.01 | Offline-verifiable signature + payload integrity check |
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
| `/v1/credentials/sign` | $0.01 | C2PA-style provenance credential for AI-generated assets (sha256 or inline bytes ≤2MB, lineage via parent_sha256) |
| `/v1/credentials/verify` | $0.01 | Signature + payload integrity + parent lineage check |
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
| `/v1/spend/check` | $0.01 | Pre-spend budget check → signed allow/deny token (`tine_ref`/`run_id` for opentine provenance binding) |
| `/v1/spend/record` | $0.01 | Idempotent spend record per tx_hash |
| `/v1/spend/ledger` | free | Per-vendor ledger read (30-day window) |

Budget enforcement with signed decision tokens: an agent can prove — cryptographically — that its spend was authorized before it happened.

### Agent Primitives (Wave 9, E25-E29 + E31-E38)

| Route | Price | Description |
|---|---|---|
| `/v1/verify/claim` | \$0.01 | Verify any claim against a source URL (fetch + rule verdict). Signed |
| `/v1/verify/action` | \$0.01 | Verify an action/outcome contract (E25). Signed |
| `/v1/resolve/outcome` | \$0.01 | Neutral outcome resolution for disputes. Signed |
| `/v1/heartbeat/*` | \$0.01 | Agent uptime monitoring: register, status, alerts, leaderboard (E26) |
| `/v1/chains` | free | Multi-chain RPC lane: 8 chains keyless (E27); `/v1/chains/rpc|address|gas` \$0.01 |
| `/v1/compliance/sanctions` | \$0.01 | Sanctions screen, PINNED list versions (OFAC+EU). Signed |
| `/v1/compliance/sanctions-delta` | \$0.01 | Sanctions delta feed since YYYY-MM-DD. Signed |
| `/v1/402/preflight` | \$0.01 | x402 challenge pre-flight: v1/v2+MPP shape verdict. Signed |
| `/v1/crypto/drainer-check` | \$0.01 | Wallet/URL drainer & abuse check (Chainabuse). Signed |
| `/v1/macro/latest` | \$0.01 | Official macro prints (CPI/NFP/unemployment, BLS). Signed |
| `/v1/ucp/verify` | \$0.01 | UCP `/.well-known/ucp` conformance verifier. Signed |
| `/v1/ap2/verify-mandates` | \$0.01 | AP2 SD-JWT+KB mandate pair verifier (signature, key binding, disclosures, constraints). Signed |
| `/v1/ap2/verify` | \$0.01 | AP2 single-mandate verify. Signed |
| `/v1/escrow/condition` | \$0.01 | Escrow-condition oracle (NO custody): release/refund/extend. Signed |
| `/v1/escrow/dispute-period` | \$0.01 | Dispute-window clock verdict. Signed |
| `/v1/export/verdict` | \$0.01 | Export-control verdict: ECCN × destination → license required? (pinned rule table + live CSL cross-check). Signed |
| `/v1/export/exceptions` | \$0.01 | Ranked license-exception finder. Signed |
| `/v1/markets/snapshot` | \$0.01 | Cross-venue prediction-market matched snapshot (Polymarket/Kalshi/Manifold/PredictIt). Signed |
| `/v1/markets/spread` | \$0.01 | Best cross-venue match: spread % + arbitrage note. Signed |
| `/v1/payroll/ledger` | \$0.01 | Sub-agent payroll ledger: multi-protocol proofs → per-worker rollups + anomaly alerts. Signed |
| `/v1/payroll/cap-check` | \$0.01 | Buyer-side budget gate: under_cap/over_cap. Signed |
| `/v1/bridges/health` | \$0.01 | Bridge-health composite: exploit history + TVL. Signed |
| `/v1/bounty/verify-deliverable` | \$0.01 | Neutral bounty-fulfillment verification. Signed |
| `/v1/bounty/payout-manifest` | \$0.01 | Payout-manifest builder with per-recipient instruction hashes. No custody |
| `/v1/llm/audit-bill` | \$0.01 | LLM bill line-item audit vs OpenRouter published pricing. Signed |
| `/v1/llm/price-lookup` | \$0.01 | Published per-token/per-1M pricing lookup. Signed |

Every verdict in this lane embeds a JWKS-verifiable Ed25519 attestation (kid `ddg-ed25519-202080d92336667a`, key at `/.well-known/ddg-attestation-jwks.json`) — the signed-verdict layer no competitor ships.

### Full catalog
See [pricing.json](https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json) for all 328 services.

## Discovery

| Surface | URL |
|---|---|
| AI manifest | `/.well-known/ai` |
| x402 discovery | `/.well-known/x402` |
| OpenAPI spec | `/openapi.json` (319 paths) |
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
