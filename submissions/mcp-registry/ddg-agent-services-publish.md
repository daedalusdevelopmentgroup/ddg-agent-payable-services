# MCP Registry publish packet — DDG Agent-Payable Services MCP

Canonical registry metadata:

```text
server.json
```

Registry name:

```text
io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp
```

Public repo:

```text
https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services
```

Last sync: `2026-06-25T16:05:00Z`

## Current status

The MCP server is source/package-ready, locally smoked over stdio, and publicly live over Streamable HTTP at `https://mcp.daedalusdevelopmentgroup.com/mcp`. `server.json` now includes a `remotes[]` entry for the hosted endpoint and validates with the official registry validation API.

Publishing is no longer blocked by endpoint readiness; it is blocked only by official MCP Registry publisher authentication/account flow (`mcp-publisher login github` or domain auth).

## Payment/distribution truth that must match other packets

- Live rails: `x402`, `direct_crypto_auto`, `direct_crypto_manual`.
- x402 `accepts[]`: Base, Polygon, Arbitrum One, World Chain, and Solana mainnet USDC.
- Direct-crypto public receiving-address families: EVM/stablecoins, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, XMR.
- MPP/Tempo is settlement-proven for tx-smoke. Keep x402/CDP facilitator settlement and indexing pending until CDP business approval/credentials or a self-hosted facilitator path proves settlement, idempotent replay, fake-token 402, and leak scan.
- CDP x402 Bazaar is not indexed/live until real CDP Facilitator settlement with `paymentPayload.resource` causes Bazaar discovery/search to return DDG.

## Validation commands

```bash
cd /path/to/ddg-agent-payable-services
python3 scripts/validate_submission_sync.py
python -m json.tool server.json >/dev/null
PYTHONDONTWRITEBYTECODE=1 DDG_MCP_AGENT_ID=ddg-mcp-stdio-smoke uv run --extra dev python scripts/smoke_mcp_server.py --transport stdio --source-tree src
PYTHONDONTWRITEBYTECODE=1 DDG_MCP_AGENT_ID=ddg-mcp-public-smoke uv run --extra dev python scripts/smoke_mcp_server.py --transport streamable-http --http-url https://mcp.daedalusdevelopmentgroup.com/mcp --agent-id ddg-mcp-public-smoke
uv build --sdist --wheel
```

If the MCP Registry validation API is available:

```bash
tmp_validate=$(mktemp)
curl -fsS -X POST https://registry.modelcontextprotocol.io/v0.1/validate \
  -H 'Content-Type: application/json' \
  --data-binary @server.json \
  -o "$tmp_validate"
python3 -m json.tool "$tmp_validate"
```

## Publish command shape

The public endpoint gate is satisfied. Use the official publisher flow from the registry repo/docs:

```bash
mcp-publisher login github
mcp-publisher publish server.json
```

The exact login method may use GitHub OAuth/OIDC or namespace verification depending on the current MCP Registry publisher release.
