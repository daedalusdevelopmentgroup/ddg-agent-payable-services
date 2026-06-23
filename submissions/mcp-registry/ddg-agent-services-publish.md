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

## Current status

The MCP server is source/package-ready and locally smoked over stdio and Streamable HTTP. The official MCP Registry submission should still wait until one of these is true:

1. `ddg-agent-services-mcp` is available from PyPI; or
2. `https://mcp.daedalusdevelopmentgroup.com/mcp` exists and passes a real MCP-client public smoke.

Do **not** publish `mcp/server.remote-template.json` as live metadata before the hosted endpoint exists.

## Validation commands

```bash
cd /path/to/ddg-agent-payable-services
python -m json.tool mcp/server.json >/dev/null
PYTHONDONTWRITEBYTECODE=1 DDG_MCP_AGENT_ID=ddg-mcp-stdio-smoke uv run --extra dev python scripts/smoke_mcp_server.py --transport stdio --source-tree src
uv build --sdist --wheel
```

If the MCP Registry validation API is available:

```bash
curl -fsS -X POST https://registry.modelcontextprotocol.io/v0.1/validate \
  -H 'Content-Type: application/json' \
  --data-binary @mcp/server.json | python3 -m json.tool
```

## Publish command shape

After the package or public endpoint gate is satisfied, use the official publisher flow from the registry repo/docs, for example:

```bash
mcp-publisher login github
mcp-publisher publish mcp/server.json
```

The exact login method may use GitHub OAuth/OIDC or namespace verification depending on the current MCP Registry publisher release.
