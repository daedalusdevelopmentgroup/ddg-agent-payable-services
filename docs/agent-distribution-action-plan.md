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
- x402scan registration started but blocked: the form read DDG metadata and found six candidate endpoints, but currently reports `0 valid resources` because live probes returned `[501] Endpoint did not return a 402 payment challenge`. See `submissions/x402scan/ddg-agent-services-registration.md`.
- x402 ecosystem/awesome-list copy: use the same registration packet and `DISCOVERY.md`.

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

1. **x402scan**
   - Started registration with `agents.daedalusdevelopmentgroup.com`.
   - Current blocker: x402scan sees `/v1/site-audit`, `/v1/model/chat-completions`, `/v1/micro-model-swarm-preview`, `/v1/model/agent-run`, `/v1/order-intake`, and `/v1/tx-smoke-test`, but gets `501` instead of `402` from all six probes.
   - Current spec preflight: OpenAPI remains canonical at `/openapi.json`; paid operations need `responses.402`, `x-payment-info.price`, `x-payment-info.protocols`, and runnable request schemas/examples; free/SIWX/nonpaid helper routes must not look paid.
   - Fix path: deploy live OpenAPI/edge behavior so paid probes return `402 payment_required` before validation, or mark non-x402/free endpoints with `security: []`, then rescan.
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
