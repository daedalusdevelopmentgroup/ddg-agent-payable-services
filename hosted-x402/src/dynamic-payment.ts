import { declareDiscoveryExtension } from "@x402/extensions/bazaar";
import { createPaymentWrapper, type x402ResourceServer } from "@x402/mcp";

export type CallServiceArgs = {
  service_id: string;
  arguments: Record<string, unknown>;
  max_spend_usd?: number;
  agent_id?: string;
};

type ToolResult = {content: Array<{type: "text"; text: string}>; isError?: boolean};

/**
 * Add native x402 MCP payment semantics to DDG's generic hosted call tool.
 *
 * Price and Bazaar metadata come from the canonical service record selected by
 * the call arguments. Free routes bypass the wrapper. Unavailable routes fail
 * before payment requirements are built. The model never receives a payment
 * header or private-key argument.
 */
export function dynamicDdgPayment(
  resourceServer: x402ResourceServer,
  options: {
    payTo: `0x${string}`;
    network?: `${string}:${string}`;
    baseUrl?: string;
    execute: (args: CallServiceArgs) => Promise<ToolResult>;
  },
): (args: CallServiceArgs, extra: unknown) => Promise<ToolResult> {
  const baseUrl = (options.baseUrl ?? "https://agents.daedalusdevelopmentgroup.com").replace(/\/$/, "");
  const network = options.network ?? "eip155:8453";
  return async (args, extra) => {
    if (!/^[A-Za-z0-9_.:\-]{1,128}$/.test(args.service_id)) {
      return {isError: true, content: [{type: "text", text: JSON.stringify({error: "unsafe_service_id"})}]};
    }
    const response = await fetch(`${baseUrl}/v1/services/${encodeURIComponent(args.service_id)}`, {
      headers: {"x-agent-id": args.agent_id ?? "ddg-hosted-mcp", "x-ddg-sdk-version": "hosted-mcp-x402/0.1.0"},
    });
    const payload = await response.json() as {service?: {path: string; price_usd: string; availability: string; description?: string}; error?: string};
    if (!response.ok || !payload.service) {
      return {isError: true, content: [{type: "text", text: JSON.stringify({error: payload.error ?? "service_not_found"})}]};
    }
    const service = payload.service;
    if (service.availability !== "available") {
      return {isError: true, content: [{type: "text", text: JSON.stringify({error: "service_unavailable", payment_accepted: false})}]};
    }
    const price = Number(service.price_usd);
    if (!Number.isFinite(price) || price < 0) {
      return {isError: true, content: [{type: "text", text: JSON.stringify({error: "invalid_catalog_price"})}]};
    }
    if (price === 0) return options.execute(args);
    if (
      args.max_spend_usd === undefined ||
      !Number.isFinite(args.max_spend_usd) ||
      args.max_spend_usd < 0 ||
      args.max_spend_usd < price
    ) {
      return {isError: true, content: [{type: "text", text: JSON.stringify({error: "max_spend_required", price_usd: price})}]};
    }
    const accepts = await resourceServer.buildPaymentRequirements({
      scheme: "exact",
      network,
      payTo: options.payTo,
      price: `$${service.price_usd}`,
      extra: {name: "USDC", version: "2"},
    });
    const paid = createPaymentWrapper(resourceServer, {
      accepts,
      resource: {url: `mcp://tool/call_service/${args.service_id}`, description: service.description ?? `Call DDG service ${args.service_id}`},
      extensions: declareDiscoveryExtension({
        toolName: "call_service",
        description: service.description ?? `Call DDG service ${args.service_id}`,
        transport: "streamable-http",
        inputSchema: {
          type: "object",
          properties: {
            service_id: {type: "string", const: args.service_id},
            arguments: {type: "object"},
            max_spend_usd: {type: "number", minimum: price},
          },
          required: ["service_id", "arguments", "max_spend_usd"],
        },
        example: {service_id: args.service_id, arguments: {}, max_spend_usd: price},
      }),
    });
    return paid(options.execute)(args, extra);
  };
}
