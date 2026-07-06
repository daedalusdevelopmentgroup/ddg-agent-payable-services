# DDG framework integrations

Put DDG in your agent's execution path. DDG is an OpenAI-compatible x402 gateway
(pay-per-call, USDC on Base) + 90+ tools. These adapters wire it into the common
agent stacks. Metered LLM routes auto-pay via x402 with a funded Base wallet
(`DDG_PRIVATE_KEY`); free/free-trial routes need none.

```bash
pip install "ddg-agent-services-mcp[openai]"
```

## LiteLLM  → `integrations/litellm/`
Register `ddg/<model>` as a LiteLLM provider — puts DDG under LangChain, CrewAI,
AutoGen, and anything else built on LiteLLM.
```python
import litellm
from ddg_litellm import register
register()
litellm.completion(model="ddg/glm-4.5-air", messages=[{"role":"user","content":"hi"}])
```

## LangChain
```python
from ddg_agent_services_mcp import create_langchain_tools
tools = create_langchain_tools(agent_id="my-agent", private_key="0x<funded base key>")
# -> pass `tools` to any LangChain agent
```

## CrewAI
```python
from ddg_agent_services_mcp import create_crewai_tools
tools = create_crewai_tools(agent_id="my-agent", private_key="0x<funded base key>")
# -> give `tools` to a CrewAI Agent
```

## OpenAI Agents SDK
```python
from ddg_agent_services_mcp import create_openai_agents_tools
tools = create_openai_agents_tools(agent_id="my-agent", private_key="0x<funded base key>")
```

## OpenAI SDK drop-in (any language)
Point `base_url` at `https://agents.daedalusdevelopmentgroup.com/v1`, or use
`create_openai_client(...)` (Python) / `ddgFetch` (TS, see `clients/typescript/`)
for automatic x402 payment.

## MCP (Claude/Cursor/Cline)
Remote: `https://mcp.daedalusdevelopmentgroup.com/mcp` · Registry:
`io.github.daedalusdevelopmentgroup/ddg-agent-services-mcp`.
