# MCP Registry publish packet — DDG Agent-Payable Services MCP

Canonical registry metadata:

```text
mcp/server.json
```

Registry name:

```text
io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp
```

Public repo:

```text
https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services
```

Last sync: `2026-06-24T01:32:05Z`

## Current status

The MCP server is source/package-ready and locally smoked over stdio and Streamable HTTP. The official MCP Registry submission should still wait until one of these is true:

1. `ddg-agent-services-mcp` is available from PyPI; or
2. `https://mcp.daedalusdevelopmentgroup.com/mcp` exists and passes a real MCP-client public smoke.

Do **not** publish `mcp/server.remote-template.json` as live metadata before the hosted endpoint exists.

## Payment/distribution truth that must match other packets

- Live rails: `x402`, `direct_crypto_auto`, `direct_crypto_manual`.
- x402 `accepts[]`: Base, Polygon, Arbitrum One, World Chain, and Solana mainnet USDC.
- Direct-crypto public receiving-address families: EVM/stablecoins, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, XMR.
- MPP/Stripe/Tempo is pending until provider env, `ready:true`, public 402 MPP advertisement, real penny settlement, idempotent replay, fake-token 402, and leak scan all pass.
- CDP x402 Bazaar is not indexed/live until real CDP Facilitator settlement with `paymentPayload.resource` causes Bazaar discovery/search to return DDG.

## Validation commands

```bash
cd /path/to/ddg-agent-payable-services
python3 scripts/validate_submission_sync.py
python -m json.tool mcp/server.json >/dev/null
PYTHONDONTWRITEBYTECODE=1 DDG_MCP_AGENT_ID=ddg-mcp-stdio-smoke uv run --extra dev python scripts/smoke_mcp_server.py --transport stdio --source-tree src
uv build --sdist --wheel
```

If the MCP Registry validation API is available:

```bash
tmp_validate=$(mktemp)
curl -fsS -X POST https://registry.modelcontextprotocol.io/v0.1/validate \
  -H 'Content-Type: application/json' \
  --data-binary @mcp/server.json \
  -o "$tmp_validate"
python3 -m json.tool "$tmp_validate"
```

## Publish command shape

After the package or public endpoint gate is satisfied, use the official publisher flow from the registry repo/docs, for example:

```bash
mcp-publisher login github
mcp-publisher publish mcp/server.json
```

The exact login method may use GitHub OAuth/OIDC or namespace verification depending on the current MCP Registry publisher release.
