# DDG Agent-Payable Services MCP security audit — 2026-06-23

Scope: public-repo MCP wrapper, package metadata, deployment templates, and local stdio/Streamable HTTP behavior.

## Summary

Verdict: **source-ready after hardening; public hosted remote still gated**.

The MCP server remains safe to publish as a stdio/package endpoint and safe to deploy behind a loopback-only Streamable HTTP service for final public smoke. Do **not** add the hosted `remotes` block to `mcp/server.json` until the public URL is deployed and passes MCP-client smoke plus leak scan.

Verification completed in this audit pass:

- Source secret/prompt/internal URL scan: **0 findings**.
- Public DDG endpoint leak scan over 8 agent-consumed surfaces: **0 findings**.
- Public payment-edge smoke: **10/10 passed**.
- Unit tests: **7 passed**.
- MCP stdio smoke: **16 tools, ok:true**.
- MCP Streamable HTTP loopback smoke: **16 tools, ok:true**.
- Package build: **sdist + wheel built successfully**.
- Python dependency audit in isolated project env: **No known vulnerabilities found** after adding security floor constraints.

## Findings and remediation

| Severity | Asset | Finding | Remediation |
| --- | --- | --- | --- |
| High | MCP payment header forwarding | Generic `Authorization` forwarding could accidentally relay unrelated Bearer/Basic/API tokens if a buyer agent passed them as `payment_headers`. | Patched: only `Authorization: Payment ...` is forwarded; Bearer/Basic and unknown auth schemes are dropped. |
| Medium | Hosted Streamable HTTP identity | Hosted MCP clients could otherwise collapse onto the server's default `DDG_MCP_AGENT_ID`, weakening order/payment scoping. | Patched: paid and agent-scoped tools accept optional `agent_id`; docs mark hosted remote as requiring buyer agent IDs. |
| Medium | Quote/path proxy surface | `ddg_quote_payment` accepted arbitrary DDG paths on the allowlisted host. | Patched: quote path is restricted to known protected DDG paths. |
| Medium | Response headers | Tool output returned all upstream response headers. | Patched: response headers are allowlisted to payment/status-safe headers only; cookies/auth/debug headers are stripped. |
| Low | Payload/resource limits | Some tool payloads could be oversized. | Patched: JSON payload cap, prompt cap, skill-scan cap, and model/order identifier validation. |
| Low | Order payload merge | `request.service_id` could override the explicit `service_id` argument. | Patched: explicit validated `service_id` wins. |
| Medium | Python transitive dependencies | `pip-audit` initially found vulnerable MCP/http transitive dependency versions in the unconstrained environment. | Patched: added security floor constraints for affected transitive packages and regenerated `uv.lock`; isolated project audit now reports no known vulnerabilities. |

## Verified controls

- No shell, eval, subprocess, arbitrary file-write, or arbitrary URL-fetch tools.
- Base URL is allowlisted and non-local upstreams must use HTTPS.
- `mcp.daedalusdevelopmentgroup.com` is not an upstream base host by default; it is reserved for the MCP server endpoint.
- Paid tools still return structured `402 payment_required` when unpaid.
- MPP is still not advertised live before provider readiness and settlement proof.
- Public hosted remote remains outside `mcp/server.json`; template is staged separately in `mcp/server.remote-template.json`.

## Required verification commands

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import json, tomllib, pathlib
for p in pathlib.Path('.').rglob('*.json'):
    if any(part in {'.git','__pycache__','.venv','dist'} for part in p.parts):
        continue
    json.loads(p.read_text(encoding='utf-8'))
with open('pyproject.toml','rb') as f:
    tomllib.load(f)
for p in pathlib.Path('.').rglob('*.py'):
    if any(part in {'.git','__pycache__','.venv','dist'} for part in p.parts):
        continue
    compile(p.read_text(encoding='utf-8'), str(p), 'exec')
print('json_toml_python_compile_ok')
PY
uv run --extra dev pytest
uv run --isolated --extra dev --with pip-audit pip-audit --progress-spinner off
PYTHONDONTWRITEBYTECODE=1 DDG_MCP_AGENT_ID=ddg-mcp-stdio-smoke uv run --extra dev python scripts/smoke_mcp_server.py --transport stdio --source-tree src
DDG_MCP_AGENT_ID=ddg-mcp-http-smoke DDG_MCP_HOST=127.0.0.1 DDG_MCP_PORT=8891 uv run --extra dev python -m ddg_agent_services_mcp --transport streamable-http
PYTHONDONTWRITEBYTECODE=1 uv run --extra dev python scripts/smoke_mcp_server.py --transport streamable-http --http-url http://127.0.0.1:8891/mcp --agent-id ddg-mcp-http-smoke
uv build --sdist --wheel
```

## Go/no-go

- Stdio/package release: **go after CI passes**.
- Public hosted MCP remote: **hold** until production loopback service, Cloudflare route, public MCP-client smoke, public leak scan, and registry metadata update all pass.
