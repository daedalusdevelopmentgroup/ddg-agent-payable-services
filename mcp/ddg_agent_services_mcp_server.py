#!/usr/bin/env python3
"""Compatibility entrypoint for the hardened DDG Agent Services MCP server.

The canonical implementation lives in ``src/ddg_agent_services_mcp/server.py``.
Keep this wrapper so older docs/scripts that execute ``mcp/ddg_agent_services_mcp_server.py``
run the same audited code path instead of a stale duplicate server.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ddg_agent_services_mcp.server import main  # noqa: E402


if __name__ == "__main__":
    main()
