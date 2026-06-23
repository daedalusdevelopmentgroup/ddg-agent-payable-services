#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Smoke-test DDG Agent-Payable Services MCP over stdio or Streamable HTTP.

This is safe for public/production readiness checks: it calls only free discovery
/status tools plus the one-cent smoke tool without payment headers, which should
return a structured 402 payment challenge. It never prints or requires secrets.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import anyio
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client

REQUIRED_TOOLS = {
    "ddg_mcp_security_profile",
    "ddg_public_resource_index",
    "ddg_fetch_public_resource",
    "ddg_agent_distribution_targets",
    "ddg_x402_bazaar_readiness",
    "ddg_x402scan_status",
    "ddg_x402_supported_chains",
    "ddg_direct_crypto_addresses",
    "ddg_micro_swarm_preview",
    "ddg_ethereum_rpc_query",
    "ddg_list_services",
    "ddg_agent_status",
    "ddg_checkout_conformance",
    "ddg_list_models",
    "ddg_list_local_runtime_options",
    "ddg_skill_safety_scan",
    "ddg_security_service_catalog",
    "ddg_order_status",
    "ddg_order_artifact",
    "ddg_receipt_verify_design",
    "ddg_tx_smoke_test",
    "ddg_quote_payment",
    "ddg_submit_order",
    "ddg_run_paid_model",
    "ddg_request_ollama_model",
}

REQUIRED_RESOURCES = {
    "ddg://manifest/ai",
    "ddg://manifest/status",
    "ddg://manifest/catalog",
    "ddg://manifest/pricing",
    "ddg://manifest/checkout-conformance",
    "ddg://manifest/refund-policy",
    "ddg://manifest/cybersecurity-services",
    "ddg://docs/llms",
    "ddg://docs/mcp-design",
    "ddg://openapi",
    "ddg://distribution/agent-radar",
    "ddg://distribution/x402-bazaar-readiness",
    "ddg://distribution/x402scan-status",
    "ddg://distribution/x402-chains",
}


def _structured(result: Any) -> dict[str, Any]:
    value = getattr(result, "structuredContent", None)
    if isinstance(value, dict):
        return value
    # Older/alternate clients may only expose text content; parse best effort.
    content = getattr(result, "content", None) or []
    if content and hasattr(content[0], "text"):
        try:
            parsed = json.loads(content[0].text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    return {"raw": str(result)[:1000]}


async def _exercise_session(session: ClientSession) -> dict[str, Any]:
    await session.initialize()
    tools_result = await session.list_tools()
    tool_names = sorted(tool.name for tool in tools_result.tools)
    missing = sorted(REQUIRED_TOOLS - set(tool_names))

    resources_result = await session.list_resources()
    resource_uris = sorted(str(resource.uri) for resource in resources_result.resources)
    missing_resources = sorted(REQUIRED_RESOURCES - set(resource_uris))
    status_resource = await session.read_resource("ddg://manifest/status")
    status_resource_text = ""
    if getattr(status_resource, "contents", None):
        first_content = status_resource.contents[0]
        status_resource_text = getattr(first_content, "text", "") or ""
    distribution_resource = await session.read_resource("ddg://distribution/agent-radar")
    distribution_resource_text = ""
    if getattr(distribution_resource, "contents", None):
        first_content = distribution_resource.contents[0]
        distribution_resource_text = getattr(first_content, "text", "") or ""

    security_profile = _structured(await session.call_tool("ddg_mcp_security_profile", {}))
    status = _structured(await session.call_tool("ddg_agent_status", {}))
    conformance = _structured(await session.call_tool("ddg_checkout_conformance", {}))
    receipt_design = _structured(
        await session.call_tool(
            "ddg_receipt_verify_design",
            {"order_id": "order-smoke-demo", "receipt_hash": "sha256-demo"},
        )
    )
    tx_smoke = _structured(await session.call_tool("ddg_tx_smoke_test", {}))
    distribution_targets = _structured(await session.call_tool("ddg_agent_distribution_targets", {}))
    bazaar_readiness = _structured(await session.call_tool("ddg_x402_bazaar_readiness", {}))
    x402scan_status = _structured(await session.call_tool("ddg_x402scan_status", {}))

    tx_body_value = tx_smoke.get("body")
    tx_body: dict[str, Any] = tx_body_value if isinstance(tx_body_value, dict) else {}
    accepted_protocols = tx_body.get("accepted_protocols") or []
    checks = {
        "tool_count_at_least_required": len(tool_names) >= len(REQUIRED_TOOLS),
        "required_tools_present": not missing,
        "security_profile_hardened": security_profile.get("status") == "source_hardened_public_remote_pending",
        "resource_count_at_least_required": len(resource_uris) >= len(REQUIRED_RESOURCES),
        "required_resources_present": not missing_resources,
        "manifest_status_resource_nonempty": len(status_resource_text) > 100 and "payment" in status_resource_text.lower(),
        "distribution_resource_mentions_x402": "x402" in distribution_resource_text.lower(),
        "distribution_targets_active": distribution_targets.get("status") == "active_distribution_work_started",
        "bazaar_not_overclaimed": str(bazaar_readiness.get("status", "")).endswith("real_cdp_settlement"),
        "x402scan_registered": x402scan_status.get("status") == "registered_live_5_resources" and len(x402scan_status.get("validated_resources", [])) >= 5,
        "agent_status_200": status.get("status") == 200,
        "checkout_conformance_200": conformance.get("status") == 200,
        "receipt_design_planned": receipt_design.get("status") == "planned_not_live",
        "tx_smoke_structured_402": tx_smoke.get("status") == 402 and tx_body.get("error") == "payment_required",
        "mpp_not_advertised_before_live": "MPP" not in [str(x).upper() for x in accepted_protocols],
    }

    return {
        "ok": all(checks.values()),
        "checks": checks,
        "missing_tools": missing,
        "missing_resources": missing_resources,
        "tool_count": len(tool_names),
        "resource_count": len(resource_uris),
        "sample": {
            "security_profile_status": security_profile.get("status"),
            "resource_count": len(resource_uris),
            "distribution_status": distribution_targets.get("status"),
            "bazaar_status": bazaar_readiness.get("status"),
            "x402scan_status": x402scan_status.get("status"),
            "x402scan_resource_count": len(x402scan_status.get("validated_resources", [])),
            "agent_status_status": status.get("status"),
            "checkout_conformance_status": conformance.get("status"),
            "receipt_design_status": receipt_design.get("status"),
            "tx_smoke_status": tx_smoke.get("status"),
            "tx_smoke_error": tx_body.get("error"),
            "tx_accepted_protocols": tx_body.get("accepted_protocols"),
        },
    }


async def smoke_stdio(args: argparse.Namespace) -> dict[str, Any]:
    env = dict(os.environ)
    env["DDG_MCP_AGENT_ID"] = args.agent_id
    env.setdefault("DDG_AGENT_SERVICES_BASE_URL", args.base_url)
    if args.source_tree:
        env["PYTHONPATH"] = args.source_tree
    command = args.stdio_command[0]
    command_args = args.stdio_command[1:]
    server = StdioServerParameters(command=command, args=command_args, env=env)
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            report = await _exercise_session(session)
            report["transport"] = "stdio"
            report["server_command"] = args.stdio_command
            return report


async def smoke_http(args: argparse.Namespace) -> dict[str, Any]:
    headers = {"X-Agent-Id": args.agent_id}
    async with streamablehttp_client(args.http_url, headers=headers, timeout=args.timeout) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            report = await _exercise_session(session)
            report["transport"] = "streamable-http"
            report["http_url"] = args.http_url
            report["session_id_present"] = bool(get_session_id())
            return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test DDG MCP server")
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    parser.add_argument("--agent-id", default="ddg-mcp-smoke")
    parser.add_argument("--base-url", default="https://agents.daedalusdevelopmentgroup.com")
    parser.add_argument("--http-url", default="http://127.0.0.1:8891/mcp")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--source-tree",
        default="src",
        help="PYTHONPATH for source-tree stdio smoke; use empty string when package is installed.",
    )
    parser.add_argument(
        "--stdio-command",
        nargs="+",
        default=[sys.executable, "-m", "ddg_agent_services_mcp"],
        help="Command used to launch stdio MCP server.",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        report = anyio.run(smoke_stdio, args)
    else:
        report = anyio.run(smoke_http, args)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
