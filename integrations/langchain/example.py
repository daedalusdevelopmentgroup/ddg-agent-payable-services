#!/usr/bin/env python3
"""DDG tools in LangChain. pip install "ddg-agent-services-mcp[openai]" langchain-core"""
from ddg_agent_services_mcp import create_langchain_tools

tools = create_langchain_tools(agent_id="my-agent", private_key="0x" + "1" * 64)
print("DDG LangChain tools:", [t.name for t in tools])
# Pass `tools` to any LangChain agent / bind_tools(...). Metered/paid tools need a funded key.
