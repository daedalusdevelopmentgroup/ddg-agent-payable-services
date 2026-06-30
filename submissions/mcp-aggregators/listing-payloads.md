# MCP aggregator listing payloads — DDG Agent-Payable Services MCP

Canonical public endpoint:

```text
https://mcp.daedalusdevelopmentgroup.com/mcp
```

Public repo:

```text
https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services
```

Name/title:

```text
DDG Agent-Payable Services MCP
```

Short description:

```text
Payment-aware MCP for DDG Agent-Payable Services: discovery, paid model routing, x402 checkout, MCP/security audits, and agent-commerce readiness resources.
```

Tags:

```text
mcp, x402, agent-commerce, machine-payments, ai-agents, security, openapi, model-context-protocol
```

Transport:

```json
{
  "type": "streamable-http",
  "url": "https://mcp.daedalusdevelopmentgroup.com/mcp"
}
```

Smithery URL publish command shape, if `SMITHERY_API_KEY`/account is available:

```bash
smithery mcp publish "https://mcp.daedalusdevelopmentgroup.com/mcp" \
  -n @daedalusdevelopmentgroup/ddg-agent-services-mcp
```

Smithery web flow:

```text
https://smithery.ai/new
URL: https://mcp.daedalusdevelopmentgroup.com/mcp
```

Glama listing signal:

```text
glama.json committed at repo root; Glama should crawl public GitHub repos and index within ~24h after review/crawl.
```

MCP.so web submission:

```text
https://mcp.so/submit
Type: MCP Server
Name: DDG Agent-Payable Services MCP
URL: https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services
Server Config: {"transport":{"type":"streamable-http","url":"https://mcp.daedalusdevelopmentgroup.com/mcp"}}
```

Official MCP Registry:

```text
mcp/server.json includes both remote Streamable HTTP and PyPI stdio metadata.
Validation endpoint returned valid:true. Publishing is account/OAuth gated through mcp-publisher.
```

## Submission status (2026-06-30)

- Official MCP Registry: **published and verified live** via GitHub Actions OIDC run https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services/actions/runs/28451913650. Registry query: https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.daedalusdevelopmentgroup%2Fddg-agent-services-mcp
- MCP.so: submit form reached at https://mcp.so/submit; submission POST is **site-login gated** (`Please Sign in to submit a server.` / `/api/submit-project`). Payload below is ready for a signed-in browser session.
- Smithery.ai: `smithery mcp publish https://mcp.daedalusdevelopmentgroup.com/mcp -n daedalusdevelopmentgroup/ddg-agent-services-mcp` reached publish flow but is **Smithery API-key gated**. Do not paste the key in chat; set it locally/securely and rerun.
- Glama: `glama.json` is committed; quick public page probe did not yet show DDG indexed. Monitor crawler/indexing.

