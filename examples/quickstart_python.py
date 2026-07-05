#!/usr/bin/env python3
"""DDG Agent-Payable Services — Python quickstart (first paid call in <5 min).

    pip install ddg-agent-services-mcp

Two paths:
  1. FREE-TRIAL / FREE routes — no wallet needed, just a stable agent id.
  2. PAID / metered routes — auto-pay via x402 with a funded Base USDC wallet.
"""
from ddg_agent_services_mcp import ddg

# ── 1) No wallet needed: free discovery + free-trial calls ──────────────────
# (private_key is only used if a call actually requires payment; a dummy is fine
#  while you're exercising free/free-trial routes.)
client = ddg(agent_id="my-agent", private_key="0x" + "1" * 64)

print("models:", len(client.get("/v1/model-catalog")["cloud_model_router"]["models"]))
print("free-trial web-search:", client.post("/v1/web-search", {"query": "x402 protocol"}).get("count"))

# ── 2) Paid / metered: auto-pays via x402 with a FUNDED Base USDC wallet ─────
#   export DDG_AGENT_ID=my-agent
#   export DDG_PRIVATE_KEY=0x<private key of a Base wallet holding a little USDC>
paid = ddg()  # reads DDG_AGENT_ID + DDG_PRIVATE_KEY from env

# OpenAI-compatible chat completion (metered, from $0.0002/call, auto-paid):
resp = paid.post("/v1/chat/completions", {
    "model": "glm-4.5-air",
    "messages": [{"role": "user", "content": "Say hello in three words."}],
})
print("chat:", resp.get("choices", [{}])[0].get("message", {}).get("content"))

# Any paid data endpoint — the 402 challenge is signed + retried automatically:
print("dex-pairs:", paid.post("/v1/dex-pairs", {"query": "WETH", "limit": 3}).get("count"))
