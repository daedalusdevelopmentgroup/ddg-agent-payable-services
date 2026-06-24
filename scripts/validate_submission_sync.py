#!/usr/bin/env python3
"""Validate DDG public listing/submission packets stay synchronized.

This is intentionally local/read-only. It does not call public endpoints or read
secrets. Run it before any x402scan, x402 ecosystem, Bazaar, MCP Registry, or
other external submission so all packets describe the same payment rails and
production gates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DIRECT_ASSETS = [
    "EVM/stablecoins",
    "BTC",
    "BCH",
    "LTC",
    "DOGE",
    "SOL",
    "TRX",
    "XRP",
    "XLM",
    "ALGO",
    "DOT",
    "ZEC",
    "XMR",
]
EXPECTED_DIRECT_ENV = [
    "DDG_CRYPTO_EVM_ADDRESS",
    "DDG_CRYPTO_BTC_ADDRESS",
    "DDG_CRYPTO_BCH_ADDRESS",
    "DDG_CRYPTO_LTC_ADDRESS",
    "DDG_CRYPTO_DOGE_ADDRESS",
    "DDG_CRYPTO_SOL_ADDRESS",
    "DDG_CRYPTO_TRX_ADDRESS",
    "DDG_CRYPTO_XRP_ADDRESS",
    "DDG_CRYPTO_XLM_ADDRESS",
    "DDG_CRYPTO_ALGO_ADDRESS",
    "DDG_CRYPTO_DOT_ADDRESS",
    "DDG_CRYPTO_ZEC_ADDRESS",
    "DDG_CRYPTO_XMR_ADDRESS",
]
EXPECTED_X402_NETWORKS = [
    "eip155:8453",
    "eip155:137",
    "eip155:42161",
    "eip155:480",
    "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",
]
REQUIRED_SUBMISSION_FILES = [
    "submissions/x402scan/ddg-agent-services-registration.md",
    "submissions/x402-ecosystem/awesome-x402-listing.md",
    "submissions/x402-bazaar/settlement-metadata.json",
    "submissions/mcp-registry/ddg-agent-services-publish.md",
    "DISCOVERY.md",
    "README.md",
    "docs/agent-distribution-action-plan.md",
    "docs/agent-distribution-targets.json",
]
STALE_PHRASES = [
    "0 valid resources",
    "HEAD currently returns 501",
    "metadata warnings until",
    "registered work started but blocked",
    "not created/pushed yet",
]


def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text())


def text(rel: str) -> str:
    return (ROOT / rel).read_text()


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def direct_assets_from_crypto_options(doc: dict[str, Any]) -> list[str] | None:
    try:
        return doc["crypto_payment_options"]["direct_crypto"]["assets"]
    except Exception:
        return None


def main() -> int:
    errors: list[str] = []

    pricing = load_json("docs/pricing.json")
    catalog = load_json("docs/agent-catalog.json")
    status = load_json("docs/agent-status.json")
    ai = load_json("docs/ai-discovery.json")
    agents = load_json("docs/agents.json")
    openapi = load_json("openapi.json")
    bazaar = load_json("docs/x402-bazaar-readiness.json")
    settlement = load_json("submissions/x402-bazaar/settlement-metadata.json")
    targets = load_json("docs/agent-distribution-targets.json")

    expect(pricing.get("payment_protocols") == ["x402", "direct_crypto_auto", "direct_crypto_manual"], "pricing payment_protocols drifted", errors)
    manual = pricing.get("direct_crypto_manual", {})
    expect(manual.get("assets") == EXPECTED_DIRECT_ASSETS, "pricing direct_crypto_manual.assets drifted", errors)
    expect(manual.get("env_addresses") == EXPECTED_DIRECT_ENV, "pricing direct_crypto_manual.env_addresses drifted", errors)
    expect(manual.get("generated_wallet_count") == 13, "pricing generated_wallet_count should be 13", errors)

    for name, doc in [("catalog", catalog), ("status", status), ("ai", ai), ("agents", agents), ("bazaar", bazaar), ("settlement", settlement)]:
        expect(direct_assets_from_crypto_options(doc) == EXPECTED_DIRECT_ASSETS, f"{name} crypto_payment_options.direct_crypto.assets drifted", errors)

    xpi = openapi.get("x-payment-info", {})
    direct = xpi.get("direct_crypto", {})
    expect(direct.get("assets") == EXPECTED_DIRECT_ASSETS, "openapi x-payment-info.direct_crypto.assets drifted", errors)
    expect(direct.get("env_addresses") == EXPECTED_DIRECT_ENV, "openapi x-payment-info.direct_crypto.env_addresses drifted", errors)
    chains = [item.get("network") for item in xpi.get("x402_supported_chains", [])]
    expect(chains == EXPECTED_X402_NETWORKS, "openapi x402_supported_chains drifted", errors)
    offer_methods = {str(offer.get("method", "")).lower() for offer in xpi.get("offers", [])}
    expect("stripe" not in offer_methods and "tempo" not in offer_methods and "mpp" not in offer_methods, "openapi top-level live offers must not include pending MPP/Stripe/Tempo", errors)
    expect(xpi.get("payment_protocols_current_public_live") == ["x402", "direct_crypto_auto", "direct_crypto_manual"], "openapi live protocol list drifted", errors)
    expect("mpp" in [str(x).lower() for x in xpi.get("payment_protocols_pending", [])], "openapi pending protocols must include mpp", errors)

    for path, path_item in openapi.get("paths", {}).items():
        post = path_item.get("post") if isinstance(path_item, dict) else None
        pinfo = post.get("x-payment-info") if isinstance(post, dict) else None
        if isinstance(pinfo, dict):
            live = [str(x).lower() for x in pinfo.get("payment_protocols_current_public_live", [])]
            pending = [str(x).lower() for x in pinfo.get("payment_protocols_pending", [])]
            expect("mpp" not in live, f"{path} must not claim MPP live", errors)
            expect("mpp" in pending, f"{path} must keep MPP pending", errors)
            expect(pinfo.get("protocols") == [{"x402": {}}], f"{path} x402scan protocols drifted", errors)

    expect(targets.get("payment_claims", {}).get("live_protocols") == ["x402", "direct_crypto_auto", "direct_crypto_manual"], "distribution targets payment claims drifted", errors)
    expect("registered_live_5_resources" in json.dumps(targets), "distribution targets lost x402scan live status", errors)

    for rel in REQUIRED_SUBMISSION_FILES:
        p = ROOT / rel
        expect(p.exists(), f"missing submission/sync file: {rel}", errors)
        body = p.read_text() if p.exists() else ""
        expect("direct_crypto_manual" in body, f"{rel} must mention direct_crypto_manual", errors)
        expect("EVM/stablecoins" in body and "XMR" in body, f"{rel} must mention the full direct-crypto family set", errors)
        expect("eip155:8453" in body or "Base" in body, f"{rel} must mention x402 Base/mainnet support", errors)
        expect("mpp" in body.lower(), f"{rel} must keep MPP status explicit", errors)
        for stale in STALE_PHRASES:
            expect(stale not in body, f"{rel} contains stale phrase: {stale}", errors)

    readme = text("README.md")
    discovery = text("DISCOVERY.md")
    expect("direct_crypto_manual" in readme and "direct_crypto_manual" in discovery, "README/DISCOVERY must mention direct_crypto_manual", errors)
    expect("ADA/Cardano is not advertised" in readme or "ADA/Cardano is not advertised" in discovery or "ADA/Cardano is **not** advertised" in text("submissions/x402scan/ddg-agent-services-registration.md"), "ADA/Cardano non-advertisement guardrail missing", errors)

    if errors:
        print("submission_sync_failed")
        for err in errors:
            print(f"- {err}")
        return 1
    print("submission_sync_ok")
    print(json.dumps({
        "direct_crypto_assets": EXPECTED_DIRECT_ASSETS,
        "x402_networks": EXPECTED_X402_NETWORKS,
        "submission_files_checked": REQUIRED_SUBMISSION_FILES,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
