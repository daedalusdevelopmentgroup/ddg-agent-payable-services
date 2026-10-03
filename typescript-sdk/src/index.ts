import { x402Client } from "@x402/core/client";
import { ExactEvmScheme } from "@x402/evm/exact/client";
import { wrapFetchWithPayment } from "@x402/fetch";
import { privateKeyToAccount, type PrivateKeyAccount } from "viem/accounts";

export type ServiceDefinition = {
  service_id: string;
  path: string;
  method: "GET" | "POST";
  price_usd: string;
  availability: "available" | "unavailable";
  fulfillment_mode: "automated" | "operator_queue" | "discovery";
  human_required: boolean;
};

export type SearchFilters = {
  objective: string;
  category?: string;
  maximum_price?: number;
  free_only?: boolean;
  automated_only?: boolean;
  availability?: "available" | "unavailable" | "any";
};

export type CallOptions = {
  /** Required for every paid operation. Never inferred from a model prompt. */
  maxSpendUsd?: number;
  idempotencyKey?: string;
};

export class DdgClient {
  readonly baseUrl: string;
  readonly agentId: string;
  readonly #fetch: typeof fetch;
  readonly #paidFetch?: typeof fetch;

  constructor(options: {
    agentId: string;
    signer?: PrivateKeyAccount;
    baseUrl?: string;
    fetchImpl?: typeof fetch;
  }) {
    if (!/^[A-Za-z0-9_.:@/+\-]{3,128}$/.test(options.agentId)) {
      throw new Error("unsafe_agent_id");
    }
    this.agentId = options.agentId;
    this.#fetch = options.fetchImpl ?? fetch;
    this.baseUrl = (options.baseUrl ?? "https://agents.daedalusdevelopmentgroup.com").replace(/\/$/, "");
    const parsed = new URL(this.baseUrl);
    if (parsed.protocol !== "https:" || parsed.username || parsed.password) {
      throw new Error("base_url_must_be_https");
    }
    if (options.signer) {
      const paymentClient = new x402Client();
      paymentClient.register("eip155:*", new ExactEvmScheme(options.signer));
      this.#paidFetch = wrapFetchWithPayment(this.#fetch, paymentClient);
    }
  }

  static fromPrivateKey(options: {agentId: string; privateKey: `0x${string}`; baseUrl?: string}): DdgClient {
    return new DdgClient({...options, signer: privateKeyToAccount(options.privateKey)});
  }

  async search(filters: SearchFilters): Promise<ServiceDefinition[]> {
    const response = await this.#request("/v1/services/search", {
      method: "POST",
      body: JSON.stringify({...filters, availability: filters.availability ?? "available"}),
    });
    const body = await response.json() as {services?: ServiceDefinition[]; error?: string};
    if (!response.ok) throw new Error(body.error ?? `http_${response.status}`);
    return body.services ?? [];
  }

  async getService(serviceId: string): Promise<ServiceDefinition> {
    if (!/^[A-Za-z0-9_.:\-]{1,128}$/.test(serviceId)) throw new Error("unsafe_service_id");
    const response = await this.#request(`/v1/services/${encodeURIComponent(serviceId)}`);
    const body = await response.json() as {service?: ServiceDefinition; error?: string};
    if (!response.ok || !body.service) throw new Error(body.error ?? `http_${response.status}`);
    return body.service;
  }

  async call<T extends Record<string, unknown>>(
    serviceId: string,
    args: Record<string, unknown>,
    options: CallOptions = {},
  ): Promise<T> {
    const service = await this.getService(serviceId);
    if (service.availability !== "available") throw new Error("service_unavailable");
    const price = Number(service.price_usd);
    if (!Number.isFinite(price) || price < 0) throw new Error("invalid_catalog_price");
    if (price > 0 && options.maxSpendUsd === undefined) throw new Error("max_spend_required");
    if (price > 0 && (!Number.isFinite(options.maxSpendUsd) || options.maxSpendUsd! < 0)) {
      throw new Error("invalid_max_spend");
    }
    if (price > 0 && options.maxSpendUsd! < price) {
      throw new Error("spend_limit_exceeded");
    }
    if (price > 0 && !this.#paidFetch) throw new Error("wallet_required");
    if (!service.path.startsWith("/") || service.path.includes("..") || service.path.includes("://")) {
      throw new Error("unsafe_service_path");
    }
    const headers: Record<string, string> = {"content-type": "application/json"};
    if (options.idempotencyKey) {
      if (!/^[A-Za-z0-9_.:\-]{1,160}$/.test(options.idempotencyKey)) throw new Error("unsafe_idempotency_key");
      headers["idempotency-key"] = options.idempotencyKey;
    }
    if (options.maxSpendUsd !== undefined) headers["x-ddg-max-spend-usd"] = String(options.maxSpendUsd);
    const request = {
      method: service.method,
      headers,
      ...(service.method === "POST" ? {body: JSON.stringify(args)} : {}),
    } satisfies RequestInit;
    const response = price > 0
      ? await this.#paidFetch!(this.baseUrl + service.path, {...request, headers: {...headers, "x-agent-id": this.agentId, "x-ddg-sdk-version": "typescript-x402/0.1.0"}})
      : await this.#request(service.path, request);
    const body = await response.json() as T & {error?: string};
    if (!response.ok) throw new Error(body.error ?? `http_${response.status}`);
    return body;
  }

  async #request(path: string, init: RequestInit = {}): Promise<Response> {
    if (!path.startsWith("/") || path.includes("..") || path.includes("://")) throw new Error("unsafe_path");
    const headers = new Headers(init.headers);
    headers.set("x-agent-id", this.agentId);
    headers.set("x-ddg-sdk-version", "typescript-x402/0.1.0");
    headers.set("accept", "application/json");
    return this.#fetch(this.baseUrl + path, {...init, headers});
  }
}
