# DDG AI-agent distribution action plan

This plan tracks the places DDG should appear so an AI agent looking for paid agent services, x402 resources, or MCP security tooling can find and evaluate us.

Last sync: `2026-06-24T01:32:05Z`

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
- x402scan/agentcash is live: `agents.daedalusdevelopmentgroup.com` is registered with 5 x402 resources.
- x402scan server page: `https://www.x402scan.com/server/c3540307-0eb2-455d-90b6-a21f7d5a3792`
- x402 ecosystem/awesome-list packet staged at `submissions/x402-ecosystem/awesome-x402-listing.md`.

Hold until additional proof:

- CDP x402 Bazaar: hold until a real CDP Facilitator **settle** call completes with Bazaar metadata and `paymentPayload.resource` set.
- Official MCP Registry: hold until the stdio package is on PyPI or the public Streamable HTTP MCP endpoint exists and has passed a real MCP-client smoke.
- MCP aggregators such as Smithery, Glama, and mcp.so: submit after official registry/PyPI or hosted MCP is not overclaimed.
- MPP/Stripe/Tempo: hold until provider env, `ready:true`, public 402 MPP advertisement, real penny settlement, replay, fake-token, and leak-scan gates all pass.

## Crypto/payment claims to keep in every packet

- Live protocols: `x402`, `direct_crypto_auto`, `direct_crypto_manual`.
- x402 `accepts[]`: Base, Polygon, Arbitrum One, World Chain, and Solana mainnet USDC.
- Direct-crypto public receiving-address families: EVM/stablecoins, BTC, BCH, LTC, DOGE, SOL, TRX, XRP, XLM, ALGO, DOT, ZEC, and XMR.
- MPP is pending, not live, until the go-live proof gates above pass.
- CDP x402 Bazaar indexing is not live until real CDP Facilitator settlement causes Bazaar discovery/search to return DDG.

## Submission sync rule

Before **any** external listing, PR, registry, or directory submission, update and revalidate the whole packet set together:

1. `openapi.json` / parent `openapi.agent-services.json`
2. `docs/pricing.json` / parent `pricing.json`
3. `docs/agent-catalog.json` / parent `agent-catalog.json`
4. `docs/agent-status.json` / parent `agent-status.json`
5. `docs/ai-discovery.json`, `docs/agents.json`, `docs/llms.txt`, and `docs/quickstart.md`
6. `submissions/x402scan/ddg-agent-services-registration.md`
7. `submissions/x402-ecosystem/awesome-x402-listing.md`
8. `submissions/x402-bazaar/settlement-metadata.json`
9. `submissions/mcp-registry/ddg-agent-services-publish.md`
10. `DISCOVERY.md`, `README.md`, and MCP distribution resources/tools

Run `python3 scripts/validate_submission_sync.py` and the tests/audits before submission.

## Agent-search keywords to match

Use these terms consistently in repo metadata, descriptions, and listing submissions:

- `x402 checkout conformance`
- `agent payment readiness audit`
- `MCP tool security audit`
- `AI agent service discovery repair`
- `buyer agent smoke probe`
- `agent-commerce OpenAPI and llms.txt proof bundle`
- `payment-aware MCP server`

## First submissions / current state

1. **x402scan / agentcash discovery**
   - Registered: `agents.daedalusdevelopmentgroup.com`.
   - Server page: `https://www.x402scan.com/server/c3540307-0eb2-455d-90b6-a21f7d5a3792`.
   - Validated resources: `/v1/site-audit`, `/v1/model/chat-completions`, `/v1/model/agent-run`, `/v1/order-intake`, `/v1/tx-smoke-test`.
   - Recheck commands after every OpenAPI/payment-edge change:
     ```bash
     npx -y @agentcash/discovery@latest discover https://agents.daedalusdevelopmentgroup.com
     npx -y @agentcash/discovery@latest check https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test
     python3 scripts/validate_submission_sync.py
     ```

2. **x402 ecosystem / awesome lists**
   - Link to GitHub repo, `DISCOVERY.md`, and the one-cent smoke route.
   - State that x402scan is live, CDP Bazaar indexing is settlement-gated, and MPP is pending.

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
python3 scripts/validate_submission_sync.py
```

Also run the public endpoint leak/payment-ladder smoke from the parent DDG payment-edge repo before claiming a public production change.
