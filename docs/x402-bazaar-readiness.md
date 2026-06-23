# x402 Bazaar readiness notes

CDP x402 Bazaar is **not** a normal directory form. Current docs say resources are indexed only after a successful CDP Facilitator **settle** call, not after verify-only and not from a manual PR.

## Ready work completed

- Created route metadata candidates in `x402-bazaar-readiness.json` and `submissions/x402-bazaar/settlement-metadata.json`.
- Added MCP `ddg_x402_bazaar_readiness` tool plus `ddg://distribution/x402-bazaar-readiness` resource so agent clients can inspect Bazaar readiness without scraping docs.
- Patched staged OpenAPI to add `info.contact.email`, remove stale MPP-live wording, remove MPP/Stripe offers from public x402 OpenAPI offers, add usable paid-route examples, and mark non-x402/free helper routes with `security: []` for x402scan-style probing.

## Remaining implementation before Bazaar appears

1. Confirm DDG x402 verifier uses CDP Facilitator settle path.
2. Add Bazaar discovery metadata to the route config for at least:
   - `/v1/tx-smoke-test`
   - `/v1/order-intake` for `buyer_agent_smoke_probe`
3. Ensure settle request includes:

```json
{
  "paymentPayload": {
    "resource": "https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test"
  }
}
```

4. Complete a real settlement.
5. Verify discovery search/catalog or the Bazaar MCP endpoint:

```bash
curl -fsS 'https://api.cdp.coinbase.com/platform/v2/x402/discovery/search?query=DDG%20checkout%20conformance&limit=20' | python3 -m json.tool
curl -fsS 'https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources?limit=100' | python3 -m json.tool
# MCP clients can also connect to:
# https://api.cdp.coinbase.com/platform/v2/x402/discovery/mcp
```

## Go/no-go

- x402scan manual registration: ready after production OpenAPI patch is deployed and scanner shows valid resources.
- CDP Bazaar: not ready until CDP settle metadata is wired and one real settlement completes.
