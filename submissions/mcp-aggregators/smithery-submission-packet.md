# Smithery.ai MCP Submission — DDG Agent-Payable Services

## Submission URL
https://smithery.ai/new

## Required Fields

**Name:** DDG Agent-Payable Services MCP

**Description:** Payment-aware MCP for DDG Agent-Payable Services: discovery, x402 checkout, MCP/security audits, paid model routing, and agent-commerce readiness resources.

**Homepage:** https://agents.daedalusdevelopmentgroup.com/.well-known/ai

**GitHub Repo:** https://github.com/daedalusdevelopmentgroup/ddg-agent-payable-services

**PyPI Package:** ddg-agent-services-mcp

**MCP Server URL:** https://mcp.daedalusdevelopmentgroup.com/mcp

**Transport:** Streamable HTTP

**Tags:** mcp, x402, agent-commerce, machine-payments, ai-agents, security, openapi, model-context-protocol

**License:** MIT

## Install Command (for Smithery CLI)
```bash
smithery mcp publish "https://mcp.daedalusdevelopmentgroup.com/mcp" \
  -n @daedalusdevelopmentgroup/ddg-agent-services-mcp
```

## Verification
- PyPI: https://pypi.org/project/ddg-agent-services-mcp/0.1.0/
- MCP endpoint: https://mcp.daedalusdevelopmentgroup.com/mcp
- OpenAPI: https://agents.daedalusdevelopmentgroup.com/openapi.json
- Status: https://agents.daedalusdevelopmentgroup.com/.well-known/ddg-agent-status.json

## Tools Exposed (15 total)
- ddg_list_services
- ddg_agent_status
- ddg_checkout_conformance
- ddg_list_models
- ddg_list_local_runtime_options
- ddg_skill_safety_scan
- ddg_security_service_catalog
- ddg_order_status
- ddg_order_artifact
- ddg_receipt_verify_design
- ddg_tx_smoke_test
- ddg_quote_payment
- ddg_submit_order
- ddg_run_paid_model
- ddg_request_ollama_model

## Payment Rails
Live: x402 (Base, Polygon, Arbitrum, World Chain, Solana USDC), direct_crypto_auto, direct_crypto_manual
Live: MPP/Tempo; Pending: Stripe/SPT

## Security Posture
- No arbitrary shell execution tools
- No file-write tools
- No provider credential relay
- Paid tools return structured 402 challenges
- All secrets redacted from public surfaces
