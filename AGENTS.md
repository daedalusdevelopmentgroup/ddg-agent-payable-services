# AGENTS.md — DDG Agent-Payable Services

This file helps AI agents (Cursor, Claude Code, autonomous agents) discover and use DDG.

**What this is:** a pay-per-call gateway for AI agents. One entry point
(`https://agents.daedalusdevelopmentgroup.com`) exposing 90+ callable tools —
utilities, blockchain RPC, market data, security audits — plus an
OpenAI-compatible LLM gateway. Payment is **x402** (USDC on Base); most routes
grant **free-trial calls per agent** (no wallet needed to start).

## Use it in 30 seconds

MCP (Claude/Cursor/Cline) — remote, no install:
```
https://mcp.daedalusdevelopmentgroup.com/mcp   (streamable-http)
```
Or via the registry: `io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp`.

Python:
```bash
pip install "ddg-agent-services-mcp[openai]"
```
```python
from ddg_agent_services_mcp import ddg, create_openai_client
ddg(agent_id="my-agent", private_key="0x"+"1"*64).get("/v1/model-catalog")  # free
# paid/metered auto-pays x402 with a funded Base USDC key:
create_openai_client(agent_id="my-agent", private_key="0x<funded>").chat.completions.create(
    model="glm-4.5-air", messages=[{"role":"user","content":"hi"}])
```

OpenAI SDK drop-in (any language): point `base_url` at
`https://agents.daedalusdevelopmentgroup.com/v1`. `GET /v1/models` is free;
`POST /v1/chat/completions` is metered (from $0.0002/call) and returns 402 until
an x402 payment header is attached.

TypeScript client: `clients/typescript/` (uses `x402-fetch` + `viem`).

## Discovery documents
- `GET /openapi.json` — full API
- `GET /llms.txt` — human/agent-readable overview
- `GET /.well-known/x402` — x402 payment manifest
- `GET /.well-known/ddg-agent-pricing.json` — per-route pricing
- `GET /v1/model-catalog` — model tiers + prices (free)

## Working in this repo
- `src/ddg_agent_services_mcp/` — MCP server + client (`tools.py`: `DDGPaidClient`, `create_openai_client`, `ddg`).
- `clients/typescript/` — TS drop-in client (`npm i` then `npm run typecheck`).
- `examples/` — runnable quickstarts (`quickstart_python.py`, `bazaar_list.py`).
- `server.json` — MCP registry manifest (published via `.github/workflows/publish-mcp.yml`).
- Build/publish Python: `uv build && uv publish`. See `QUICKSTART.md`.
