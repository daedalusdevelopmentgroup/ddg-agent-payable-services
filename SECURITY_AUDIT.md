# Pre-publish Security Audit Summary

Date: 2026-06-23

This repository packet was re-audited before publishing DDG Agent-Payable Services to GitHub and agent-discovery surfaces.

## Checks performed

- JSON parse validation for all repository `*.json` files.
- Python source compile validation without writing bytecode.
- Secret-pattern scan for private-key blocks, API keys, Stripe live keys, AWS keys, GitHub tokens, private-key hex labels, LAN URLs, loopback verifier URLs, and unsafe raw-provider-account wording.
- Git hygiene check for clean status and no `Co-authored-by:` trailers.
- Public production payment ladder check:
  - no identity -> `403 agent_only`
  - identity/no payment -> `402 payment_required`
  - fake payment -> `402 payment_required`
- Node sidecar supply-chain audit in the source workspace: `npm audit --omit=dev` returned zero vulnerabilities.
- MCP package readiness checks: stdio package metadata staged, local free-tool/402 smoke performed, and hosted HTTP/Streamable MCP intentionally not listed as live until deployed and smoked.
- Wallet/public-chain audit: published service wallets showed zero public tx/balance seen in the latest public-data scan; XMR and DOT have the noted visibility limitations.

## Result

- Confirmed secret leaks: **0**
- Public live endpoint confirmed leaks: **0**
- Public repo packet confirmed secret/loopback/LAN leaks: **0**
- `Co-authored-by:` commit trailers in this packet repo: **0**
- Tracked `__pycache__` / `*.pyc` / `*.env` / `c_priv` / `node_modules`: **0**
- JSON validation: **pass**
- Python compile validation: **pass**
- Public ladder: **pass**
- `npm audit --omit=dev`: **0 vulnerabilities**

## Reviewed non-leak findings

The scan may flag DDG's explicit policy language such as "not resale of raw provider accounts" or "never raw provider account/session access." Those are benign safety statements, not credential leaks or resale claims.

## Important live-rail status

Current public live rails are:

```text
x402
direct_crypto_auto
```

MPP/Stripe/Tempo is installed but **not advertised live**. It must not be listed as live until a real penny-scale MPP payment settles, idempotency replay passes, fake-token failure stays closed, sidecar health reports `ready:true`, and public docs/status are updated.

## Security stance

DDG sells bounded artifacts/results, not raw provider account access. DDG does not publish or return raw provider API keys, OAuth tokens, private account sessions, private model IDs, payment private keys, raw payment tokens, or verifier sidecar URLs.
