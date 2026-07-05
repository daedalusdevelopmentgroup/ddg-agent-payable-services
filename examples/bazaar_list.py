#!/usr/bin/env python3
"""Light up DDG resources on the Coinbase x402 Bazaar.

The Bazaar lists a resource automatically the first time a payment for it is
*settled* through the CDP facilitator. This script performs one real, buyer-funded
settlement per resource through CDP, which catalogs it (appears in ~10 min).

Requires (all yours to provide):
  export CDP_API_KEY_ID=...           # portal.cdp.coinbase.com -> API keys
  export CDP_API_KEY_SECRET=...
  export BAZAAR_BUYER_PRIVATE_KEY=0x  # a Base wallet holding a little USDC (each
                                      # listing spends the route price, e.g. $0.002-$0.03)

    pip install "x402[evm]" cdp-sdk requests
    python bazaar_list.py            # lists the FLAGSHIP set below

NOTE: each settlement moves real USDC from your buyer wallet to DDG's payTo
(you paying yourself, minus any gas). Start with a few flagship routes.
"""
import json
import os
import sys
import requests
from eth_account import Account
from x402 import x402ClientSync
from x402.http.x402_http_client import x402HTTPClientSync
from x402.mechanisms.evm.exact import ExactEvmScheme
from cdp.auth.utils.http import GetAuthHeadersOptions, get_auth_headers

BASE = "https://agents.daedalusdevelopmentgroup.com"
CDP_HOST = "api.cdp.coinbase.com"
CDP_SETTLE_PATH = "/platform/v2/x402/settle"

# Flagship routes to list first (broad + differentiated). Add more once these land.
FLAGSHIP = [
    "/v1/dex-pairs", "/v1/prediction-markets", "/v1/stock-price", "/v1/fx-rate",
    "/v1/chat/completions", "/v1/ethereum/rpc", "/v1/mcp-tool-security-audit",
    "/v1/prompt-injection-scan", "/v1/site-audit", "/v1/web-search",
]

def _need(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env {k} (see header).")
    return v

def main():
    cdp_id = _need("CDP_API_KEY_ID")
    cdp_secret = _need("CDP_API_KEY_SECRET")
    buyer = Account.from_key(_need("BAZAAR_BUYER_PRIVATE_KEY"))
    paths = sys.argv[1:] or FLAGSHIP

    xc = x402ClientSync()
    xc.register("eip155:8453", ExactEvmScheme(signer=buyer))
    xh = x402HTTPClientSync(xc)
    print(f"buyer {buyer.address} -> settling {len(paths)} resource(s) via CDP facilitator\n")

    for path in paths:
        try:
            r = requests.post(f"{BASE}{path}", json={"bazaar": "list"},
                              headers={"content-type": "application/json"}, timeout=40)
            if r.status_code != 402:
                print(f"  ~ {path}: expected 402, got {r.status_code} (skipped)"); continue
            pr = xh.get_payment_required_response(lambda k: r.headers.get(k), r.content)
            payload = xh.create_payment_payload(pr)
            requirements = pr.accepts[0]
            body = {
                "paymentPayload": payload.model_dump(by_alias=True, mode="json"),
                "paymentRequirements": requirements.model_dump(by_alias=True, mode="json"),
            }
            headers = get_auth_headers(GetAuthHeadersOptions(
                api_key_id=cdp_id, api_key_secret=cdp_secret,
                request_method="POST", request_host=CDP_HOST,
                request_path=CDP_SETTLE_PATH, request_body=body,
            ))
            headers["Content-Type"] = "application/json"
            s = requests.post(f"https://{CDP_HOST}{CDP_SETTLE_PATH}", json=body, headers=headers, timeout=60)
            ok = s.status_code == 200 and s.json().get("success", s.json().get("settled"))
            print(f"  {'✓' if ok else '✗'} {path}: settle HTTP {s.status_code} {str(s.text)[:160]}")
        except Exception as e:
            print(f"  ✗ {path}: {type(e).__name__}: {e}")

    print("\nCheck listings (~10 min): "
          "curl -s https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources "
          "| grep daedalus")

if __name__ == "__main__":
    main()
