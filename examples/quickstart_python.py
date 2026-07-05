#!/usr/bin/env python3
"""DDG Agent-Payable Services — Python quickstart (first paid call in <5 min).

    pip install "ddg-agent-services-mcp[openai]"

Three ways in:
  1. FREE / free-trial routes — no wallet needed, just a stable agent id.
  2. DDGPaidClient  — any DDG endpoint; auto-signs + pays the x402 402 challenge.
  3. create_openai_client — a real openai.OpenAI drop-in that auto-pays.

Paid/metered routes settle in USDC on Base, so set a FUNDED wallet key:
    export DDG_AGENT_ID=my-agent
    export DDG_PRIVATE_KEY=0x<private key of a Base wallet holding a little USDC>
"""
import os
from ddg_agent_services_mcp import ddg, create_openai_client

# ── 1) No wallet needed: free discovery + free-trial calls ──────────────────
client = ddg(agent_id="my-agent", private_key="0x" + "1" * 64)  # key unused until a call needs payment
print("models:", len(client.get("/v1/model-catalog")["cloud_model_router"]["models"]))
print("free-trial web-search:", client.post("/v1/web-search", {"query": "x402 protocol"}).get("count"))

# ── 2) DDGPaidClient — auto-pays x402 on any endpoint (needs a funded key) ───
paid = ddg()  # reads DDG_AGENT_ID + DDG_PRIVATE_KEY from env
print("dex-pairs:", paid.post("/v1/dex-pairs", {"query": "WETH", "limit": 3}).get("count"))

# ── 3) OpenAI SDK drop-in — chat.completions.create() auto-pays ──────────────
oai = create_openai_client(agent_id=os.environ["DDG_AGENT_ID"], private_key=os.environ["DDG_PRIVATE_KEY"])
resp = oai.chat.completions.create(
    model="glm-4.5-air",
    messages=[{"role": "user", "content": "Say hello in three words."}],
)
print("chat:", resp.choices[0].message.content)
