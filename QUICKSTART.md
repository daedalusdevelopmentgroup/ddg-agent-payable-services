# DDG Agent-Payable Services — Quickstart (first paid call in <5 min)

Base URL: `https://agents.daedalusdevelopmentgroup.com` · Pay-per-call via **x402** (USDC on Base). Most routes grant **free trial calls per agent** (no wallet needed to start).

## Python
```bash
pip install ddg-agent-services-mcp
```
```python
from ddg_agent_services_mcp import ddg
c = ddg(agent_id="my-agent", private_key="0x" + "1"*64)   # dummy key ok for free/free-trial
c.get("/v1/model-catalog")                                 # free
c.post("/v1/web-search", {"query": "x402 protocol"})       # free-trial

# Paid/metered — auto-pays x402 with a FUNDED Base USDC wallet:
#   export DDG_AGENT_ID=my-agent DDG_PRIVATE_KEY=0x<funded base key>
paid = ddg()
paid.post("/v1/chat/completions", {"model": "glm-4.5-air",
    "messages": [{"role": "user", "content": "hi"}]})       # OpenAI-shaped, metered
```

## TypeScript
```bash
npm i x402-fetch viem   # then use clients/typescript/ddg.ts
```
See `clients/typescript/` (DDGClient + `ddgFetch` OpenAI-SDK drop-in).

## OpenAI SDK drop-in (any language)
Point the OpenAI SDK at `https://agents.daedalusdevelopmentgroup.com/v1`; `GET /v1/models` is free; `POST /v1/chat/completions` is metered (from $0.0002/call, no cap) and returns 402 until an x402 payment header is attached (the clients above do this automatically).

## The x402 flow (what the clients automate)
1. Call an endpoint → `402 Payment Required` with an x402 v2 challenge (`accepts[]`: Base USDC, amount, payTo).
2. Sign an EIP-3009 USDC authorization for that amount with your Base wallet.
3. Retry with the `X-PAYMENT` header → `200` + result + receipt.
