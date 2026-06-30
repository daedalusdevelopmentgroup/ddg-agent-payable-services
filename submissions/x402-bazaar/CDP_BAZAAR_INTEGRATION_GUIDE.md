# CDP x402 Bazaar Integration Guide

## Current Status
- x402scan registered and live with 5 validated resources
- CDP Bazaar metadata staged but NOT indexed until real settlement

## What CDP Bazaar Needs

1. **Real CDP Facilitator settlement** (not just verify)
2. **`paymentPayload.resource` set to the exact public resource URL**
3. **Bazaar discovery metadata in extensions.bazaar**

## Implementation Steps

### Step 1: Wire Bazaar metadata into x402 verifier

Add to `x402_verifier_sidecar.py` or payment edge scaffold:

```python
# On settle response, include Bazaar metadata
bazaar_metadata = {
    "resource": "https://agents.daedalusdevelopmentgroup.com/v1/tx-smoke-test",
    "name": "DDG Agent-Payable Services",
    "description": "AI-agent-native checkout/payment conformance, MCP/tool security audits, agent-discovery repair",
    "category": "developer_tools",
    "tags": ["x402", "agent-commerce", "mcp", "security", "openapi"],
    "pricing": {
        "type": "per_use",
        "currency": "USDC",
        "amount": "0.01"
    },
    "discovery": {
        "openapi": "https://agents.daedalusdevelopmentgroup.com/openapi.json",
        "llms_txt": "https://agents.daedalusdevelopmentgroup.com/llms.txt",
        "ai_discovery": "https://agents.daedalusdevelopmentgroup.com/.well-known/ai"
    }
}
```

### Step 2: Complete one real penny settlement

Use the CDP Facilitator SDK or direct API:

```bash
# Example using CDP Facilitator
# 1. Get 402 challenge from DDG
# 2. Create payment payload with Bazaar metadata
# 3. Call CDP verify then settle
# 4. Verify Bazaar indexing via CDP discovery API
```

### Step 3: Verify Bazaar indexing

After settlement, check:
- `https://api.cdp.coinbase.com/platform/v2/x402/discovery/mcp`
- Search for "DDG" or "daedalusdevelopmentgroup"

## Resources
- CDP x402 Docs: https://docs.cdp.coinbase.com/x402/
- CDP Bazaar: https://docs.cdp.coinbase.com/x402/bazaar
- x402scan: https://www.x402scan.com/server/c3540307-0eb2-455d-90b6-a21f7d5a3792

## Next Action Required
Need operator to:
1. Confirm CDP Facilitator credentials/API key availability
2. Run one real $0.01 settlement via CDP Facilitator with Bazaar metadata
3. Verify DDG appears in Bazaar discovery
