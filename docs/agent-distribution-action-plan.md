# DDG AI-agent distribution action plan

This plan tracks the places DDG should appear so an AI agent looking for paid agent services, x402 resources, or MCP security tooling can find and evaluate us.

## Current go/no-go

Ready to use now:

- Public GitHub repo: `https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services`
- Owned machine-readable surfaces:
  - `https://agents.daedalusdevelopmentgroup.com/.well-known/ai`
  - `https://agents.daedalusdevelopmentgroup.com/llms.txt`
  - `https://agents.daedalusdevelopmentgroup.com/openapi.json`
  - `https://agents.daedalusdevelopmentgroup.com/.well-known/agent-catalog.json`
  - `https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-pricing.json`
  - `https://agents.daedalusdevelopmentgroup.com/.well-known/agent-skills/index.json`
- x402scan/agentcash is now live: `agents.daedalusdevelopmentgroup.com` registered 5 x402 resources on x402scan, and AgentCash discovery/check pass against the live origin.
- x402scan server page: `https://www.x402scan.com/server/c3540307-0eb2-455d-90b6-a21f7d5a3792`
- x402 ecosystem/awesome-list packet staged at `submissions/x402-ecosystem/awesome-x402-listing.md`.

Hold until additional proof:

- CDP x402 Bazaar: hold until a real CDP Facilitator **settle** call completes with Bazaar metadata and `paymentPayload.resource` set.
- Official MCP Registry: hold until the stdio package is on PyPI or the public Streamable HTTP MCP endpoint exists and has passed a real MCP-client smoke.
- MCP aggregators such as Smithery, Glama, and mcp.so: submit after official registry/PyPI or hosted MCP is not overclaimed.

## Agent-search keywords to match

Use these terms consistently in repo metadata, descriptions, and listing submissions:

- `x402 checkout conformance`
- `agent payment readiness audit`
- `MCP tool security audit`
- `AI agent service discovery repair`
- `buyer agent smoke probe`
- `agent-commerce OpenAPI and llms.txt proof bundle`
- `payment-aware MCP server`

## First submissions to start

1. **x402scan / agentcash discovery**
   - Started registration with `agents.daedalusdevelopmentgroup.com`.
   - Earlier UI attempt reported `0 valid resources` with `[501] Endpoint did not return a 402 payment challenge`.
   - Fresh CLI preflight now succeeds against the live origin: `agentcash discover` reads 17 routes from OpenAPI and `agentcash check https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test` classifies the one-cent smoke route as paid.
   - Remaining warnings are metadata/deploy drift: live OpenAPI is missing `info.contact`, `info.x-guidance`, `x-payment-info.price`, and `x-payment-info.protocols`; this source branch patches those fields and removes paid-looking `x-payment-info` from the free swarm-preview route.
   - Deploy source OpenAPI/edge behavior, then rescan/register.
   - Recheck commands after deploy:
     ```bash
     npx -y @agentcash/discovery@latest discover https://agents.daedalusdevelopmentgroup.com
     npx -y @agentcash/discovery@latest check https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test
     ```
   - First target after fix: `https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test`.

2. **x402 ecosystem / awesome lists**
   - Link to GitHub repo, `DISCOVERY.md`, and the one-cent smoke route.
   - State that CDP Bazaar indexing is pending real settlement, not already live.

3. **Official MCP Registry**
   - Validate `mcp/server.json` first.
   - Publish only package/stdin metadata until either PyPI package upload or hosted MCP endpoint exists.
   - Do not publish `mcp/server.remote-template.json` as live registry metadata.

## Re-audit required before every external listing

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --extra dev pytest
PYTHONDONTWRITEBYTECODE=1 DDG_MCP_AGENT_ID=ddg-mcp-stdio-smoke uv run --extra dev python scripts/smoke_mcp_server.py --transport stdio --source-tree src
uv run --isolated --extra dev --with pip-audit pip-audit --progress-spinner off
```

Also run the public endpoint leak/payment-ladder smoke from the parent DDG payment-edge repo before claiming a public production change.
