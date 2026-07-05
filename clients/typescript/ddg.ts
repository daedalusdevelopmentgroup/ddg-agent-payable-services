/**
 * DDG Agent-Payable Services — TypeScript drop-in client.
 *
 *   npm i x402-fetch viem
 *
 * Free / free-trial routes need no wallet (just an agent id). Paid + metered
 * routes are auto-paid via x402 when you pass a funded Base USDC wallet key.
 */
import { wrapFetchWithPayment } from "x402-fetch";
import { privateKeyToAccount } from "viem/accounts";

const DEFAULT_BASE = "https://agents.daedalusdevelopmentgroup.com";

export interface DDGOptions {
  agentId: string;
  /** 0x-prefixed private key of a Base wallet holding a little USDC. Omit for free/free-trial only. */
  privateKey?: `0x${string}`;
  baseUrl?: string;
}

export class DDGClient {
  private base: string;
  private agentId: string;
  private fetchImpl: typeof fetch;

  constructor(opts: DDGOptions) {
    this.base = (opts.baseUrl ?? DEFAULT_BASE).replace(/\/$/, "");
    this.agentId = opts.agentId;
    // If a key is provided, wrap fetch so x402 402-challenges are signed + retried automatically.
    this.fetchImpl = opts.privateKey
      ? (wrapFetchWithPayment(fetch, privateKeyToAccount(opts.privateKey)) as typeof fetch)
      : fetch;
  }

  /** POST a JSON body to a DDG endpoint; auto-pays x402 if a key was provided. */
  async post<T = unknown>(path: string, body: Record<string, unknown> = {}): Promise<T> {
    const r = await this.fetchImpl(`${this.base}${path}`, {
      method: "POST",
      headers: { "content-type": "application/json", "x-agent-id": this.agentId },
      body: JSON.stringify(body),
    });
    return (await r.json()) as T;
  }

  /** GET a free DDG endpoint (e.g. /v1/model-catalog, /v1/models). */
  async get<T = unknown>(path: string): Promise<T> {
    const r = await this.fetchImpl(`${this.base}${path}`, { headers: { "x-agent-id": this.agentId } });
    return (await r.json()) as T;
  }
}

/**
 * OpenAI-compatible: returns a `fetch` that auto-pays x402, for use as the
 * OpenAI SDK's `fetch` option:
 *   const openai = new OpenAI({ baseURL: `${DEFAULT_BASE}/v1`, apiKey: "x402",
 *     fetch: ddgFetch(privateKey), defaultHeaders: { "x-agent-id": "my-agent" } });
 */
export function ddgFetch(privateKey: `0x${string}`): typeof fetch {
  return wrapFetchWithPayment(fetch, privateKeyToAccount(privateKey)) as typeof fetch;
}
