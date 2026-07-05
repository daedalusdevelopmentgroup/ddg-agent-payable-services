/**
 * DDG Agent-Payable Services — TypeScript quickstart (first paid call in <5 min).
 *   npm i x402-fetch viem && npx tsx quickstart.ts
 */
import { DDGClient } from "./ddg.ts";

// 1) FREE / free-trial — no wallet needed, just an agent id.
const free = new DDGClient({ agentId: "my-agent" });
const cat = await free.get<{ cloud_model_router: { models: unknown[] } }>("/v1/model-catalog");
console.log("models:", cat.cloud_model_router.models.length);
const search = await free.post<{ count?: number }>("/v1/web-search", { query: "x402 protocol" });
console.log("free-trial web-search count:", search.count);

// 2) PAID / metered — auto-pays via x402 with a FUNDED Base USDC wallet.
//    export DDG_PRIVATE_KEY=0x<private key of a Base wallet holding a little USDC>
const paid = new DDGClient({
  agentId: "my-agent",
  privateKey: process.env.DDG_PRIVATE_KEY as `0x${string}`,
});
const chat = await paid.post<{ choices?: { message?: { content?: string } }[] }>(
  "/v1/chat/completions",
  { model: "glm-4.5-air", messages: [{ role: "user", content: "Say hello in three words." }] },
);
console.log("chat:", chat.choices?.[0]?.message?.content);
