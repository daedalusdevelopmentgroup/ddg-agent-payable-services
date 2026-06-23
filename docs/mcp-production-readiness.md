# MCP production readiness and go-live checklist

DDG's MCP wrapper is payment-aware: free tools expose discovery/status/conformance, and paid tools return structured `402 payment_required` payloads from the DDG payment edge unless the caller supplies valid payment headers.

## Current status

- Stdio/package path: source-ready and locally smoked.
- Streamable HTTP server: source-ready and locally smoked on `http://127.0.0.1:8891/mcp`.
- Public hosted MCP endpoint: **not live yet**; do not publish a `remotes` entry in `mcp/server.json` until the public URL is deployed and MCP-client smoked.
- Current live payment rails exposed through MCP paid tools: `x402`, `direct_crypto_auto`.
- MPP remains pending until provider env + `ready:true` + penny settlement proof.

## Local smoke commands

### Stdio

```bash
cd /path/to/ddg-agent-payable-services
PYTHONDONTWRITEBYTECODE=1 \
DDG_MCP_AGENT_ID=ddg-mcp-stdio-smoke \
PYTHONPATH=src \
uv run --extra dev python scripts/smoke_mcp_server.py --transport stdio --source-tree src
```

Expected: `ok: true`, 18 tools and 9 resources present, `ddg_mcp_security_profile` reports `source_hardened_public_remote_pending`, `ddg://manifest/status` reads successfully, `ddg_agent_status` returns 200, and `ddg_tx_smoke_test` returns structured 402.

### Streamable HTTP, local only

Terminal 1:

```bash
cd /path/to/ddg-agent-payable-services
PYTHONPATH=src \
DDG_MCP_AGENT_ID=ddg-mcp-http-local \
DDG_MCP_HOST=127.0.0.1 \
DDG_MCP_PORT=8891 \
uv run --extra dev python -m ddg_agent_services_mcp --transport streamable-http
```

Terminal 2:

```bash
uv run --extra dev python scripts/smoke_mcp_server.py \
  --transport streamable-http \
  --http-url http://127.0.0.1:8891/mcp \
  --agent-id ddg-mcp-http-smoke
```

Expected: `ok: true`, 18 tools and 9 resources present, and unpaid paid-tool call returns structured 402 with `accepted_protocols` containing only currently live rails.

## Production deployment path

1. Clone/pull the public repo on the production host, for example:

   ```text
   /srv/ddg-agent-services-mcp/ddg-agent-payable-services
   ```

2. Install/copy the systemd template:

   ```bash
   sudo install -m 0644 deploy/systemd/ddg-agent-services-mcp.service \
     /etc/systemd/system/ddg-agent-services-mcp.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now ddg-agent-services-mcp.service
   ```

3. Verify loopback MCP with a real MCP client:

   ```bash
   uv run --extra dev python scripts/smoke_mcp_server.py \
     --transport streamable-http \
     --http-url http://127.0.0.1:8891/mcp \
     --agent-id ddg-mcp-prod-loopback-smoke
   ```

4. Add Cloudflare Tunnel ingress, preferably on a dedicated hostname:

   ```text
   https://mcp.daedalusdevelopmentgroup.com/mcp
   ```

   See `deploy/cloudflare/ddg-agent-services-mcp-ingress.example.yml`.

5. Smoke the public URL with the same script:

   ```bash
   uv run --extra dev python scripts/smoke_mcp_server.py \
     --transport streamable-http \
     --http-url https://mcp.daedalusdevelopmentgroup.com/mcp \
     --agent-id ddg-mcp-public-smoke
   ```

6. Run public leak and payment-ladder checks again before advertising the remote endpoint.

7. Only after the public smoke passes, add a `remotes` entry to `mcp/server.json` and submit/update the official MCP Registry package metadata.

## Security constraints

- No arbitrary shell/eval/file-write tools.
- No raw provider credentials, OAuth sessions, private model IDs, raw payment tokens, or verifier loopback URLs in tool output.
- Generic `Authorization: Bearer/Basic/...` values are dropped; only `Authorization: Payment ...` is forwarded as payment material.
- Response headers are allowlisted; cookies/auth/debug headers are stripped.
- Response bodies/resources are size-capped and redacted for secret-like keys/values.
- MCP resources are fixed `ddg://` public manifests/docs only; arbitrary URLs and paths are rejected.
- Hosted/remote buyers must pass stable `agent_id` values on paid/order-scoped tools.
- MCP service listens on loopback behind Cloudflare; direct public access should go through the tunnel/WAF only.
- Public paid tools should return DDG's structured payment challenges rather than opaque MCP errors.
- MPP must remain pending in outputs until public 402 challenges include MPP and real settlement proof passes.

## Go/no-go

Production-ready source status: **yes** for stdio and local Streamable HTTP.

Public-live hosted MCP status: **hold** until loopback service deployment, Cloudflare route, public MCP-client smoke, and public leak scan all pass.
