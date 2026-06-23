#!/usr/bin/env python3
"""Minimal buyer-agent discovery client for DDG Agent-Payable Services."""
import json
import urllib.request

BASE = "https://agents.daedalusdevelopmentgroup.com"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=20) as resp:
        return resp.status, json.loads(resp.read().decode())

for path in [
    "/.well-known/ddg-agent-status.json",
    "/.well-known/ddg-agent-pricing.json",
    "/.well-known/agent-catalog.json",
    "/.well-known/ddg-agent-checkout-conformance.json",
]:
    status, body = get(path)
    print(path, status, body.get("schema_version") or body.get("status") or body.get("service"))
