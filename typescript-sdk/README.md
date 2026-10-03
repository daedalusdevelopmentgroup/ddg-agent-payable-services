# `@daedalusdevelopmentgroup/ddg-x402`

A wallet-side TypeScript SDK for the canonical DDG service catalog. Importing
the package performs no network request. Paid calls require both a signer and
an explicit `maxSpendUsd`; the value is checked against canonical service
metadata in code before the x402 wrapper can sign.

```ts
import { DdgClient } from "@daedalusdevelopmentgroup/ddg-x402";

const client = DdgClient.fromPrivateKey({
  agentId: "my-agent",
  privateKey: process.env.EVM_PRIVATE_KEY as `0x${string}`,
});

const candidates = await client.search({objective: "verify OpenTine provenance", free_only: true});
const result = await client.call("tine_diff_explain", {tine_a, tine_b}, {maxSpendUsd: 0.01});
```

