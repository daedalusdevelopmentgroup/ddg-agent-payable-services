# DDG x402 — TypeScript client

Drop-in client for [DDG Agent-Payable Services](https://agents.daedalusdevelopmentgroup.com). Free/free-trial routes need no wallet; paid + metered routes auto-pay via x402 with a funded Base USDC wallet.

```bash
npm i x402-fetch viem
```

```ts
import { DDGClient } from "./ddg.ts";

// Free + free-trial (no wallet):
const c = new DDGClient({ agentId: "my-agent" });
await c.get("/v1/model-catalog");
await c.post("/v1/web-search", { query: "x402 protocol" });

// Paid / metered (auto-pays x402 with a funded Base USDC key):
const paid = new DDGClient({ agentId: "my-agent", privateKey: process.env.DDG_PRIVATE_KEY as `0x${string}` });
await paid.post("/v1/chat/completions", { model: "glm-4.5-air", messages: [{ role: "user", content: "hi" }] });
```

OpenAI SDK drop-in: pass `ddgFetch(privateKey)` as the OpenAI client's `fetch`, with `baseURL` `https://agents.daedalusdevelopmentgroup.com/v1`.
