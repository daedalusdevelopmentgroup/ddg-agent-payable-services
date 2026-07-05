"""DDG Agent-Payable Services — MCP server + multi-framework tool wrappers.

Provides:
- MCP server (ddg_agent_services_mcp.server) for Claude/Cursor/Hermes
- Framework tool wrappers (ddg_agent_services_mcp.tools) for LangChain,
  CrewAI, OpenAI Agents SDK, AutoGen, PydanticAI, LlamaIndex, Google ADK
- OpenAI-compatible gateway (create_openai_client) — drop-in for openai-python
- One-liner factory (ddg) — simplest possible entry point
- Shared DDGPaidClient that handles x402 payment challenges automatically
"""
__version__ = "0.4.0"


def __getattr__(name: str):
    """Lazy import to avoid forcing requests/x402/eth-account deps when only
    the MCP server is needed (e.g. ``from ddg_agent_services_mcp import server``)."""
    if name in ("ddg", "DDGPaidClient", "create_openai_client"):
        from importlib import import_module
        tools = import_module(".tools", __package__)
        return getattr(tools, name)
    raise AttributeError(f"module 'ddg_agent_services_mcp' has no attribute {name!r}")


__all__ = ["ddg", "DDGPaidClient", "create_openai_client"]

