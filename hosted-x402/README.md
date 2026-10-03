# Hosted MCP x402 wrapper

This module is the hosted counterpart to the Python buyer profile. It uses the
official `@x402/mcp` server wrapper and Bazaar discovery extension. The wrapper
loads the canonical service record selected by `call_service`, refuses
unavailable services before payment, enforces `max_spend_usd`, builds the exact
price requirement, and only then executes the DDG HTTP call.

Stdio remains wallet-side and signs locally. Hosted deployments must register
`dynamicDdgPayment(...)` as the `call_service` handler; they must not expose
payment headers or wallet keys in the MCP input schema.

