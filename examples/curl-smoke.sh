#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-https://agents.daedalusdevelopmentgroup.com}"
AGENT_ID="${AGENT_ID:-example-buyer-agent}"

status_json="$(mktemp)"
catalog_json="$(mktemp)"
curl -fsS -o "$status_json" "$BASE/.well-known/ddg-agent-status.json"
python3 -m json.tool "$status_json"
curl -fsS -o "$catalog_json" "$BASE/.well-known/agent-catalog.json"
python3 -m json.tool "$catalog_json" >/dev/null
curl -i -X POST "$BASE/v1/tx-smoke-test"   -H 'Content-Type: application/json'   -H "X-Agent-Id: $AGENT_ID"   -d '{"service":"tx_penny_smoke_test"}'
