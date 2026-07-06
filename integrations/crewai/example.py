#!/usr/bin/env python3
"""DDG tools in CrewAI. pip install "ddg-agent-services-mcp[openai]" crewai-tools"""
from ddg_agent_services_mcp import create_crewai_tools

tools = create_crewai_tools(agent_id="my-agent", private_key="0x" + "1" * 64)
print("DDG CrewAI tools:", len(tools))
# Give `tools` to a CrewAI Agent(tools=tools, ...). Metered/paid tools need a funded key.
