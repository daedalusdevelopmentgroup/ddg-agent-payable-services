#!/usr/bin/env python3
"""Run an agent-checkout conformance probe against the DDG payment edge.

The default mode performs non-spending checks only: identity gate, 402 challenge,
and fake-token fail-closed. Pass --mock-payment-token for local/dev edge tests or
--paid-credential-* options for a real provider test when you intentionally want
to create an order.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class CheckResult:
    id: str
    ok: bool
    status: int | None
    expected: str
    detail: str
    response_excerpt: Any | None = None


def _json_body(data: dict[str, Any]) -> bytes:
    return json.dumps(data, separators=(",", ":")).encode()


def _request(method: str, url: str, headers: dict[str, str] | None = None, body: dict[str, Any] | None = None) -> tuple[int, dict[str, str], Any]:
    req = urllib.request.Request(url, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    data = None
    if body is not None:
        data = _json_body(body)
        req.add_header('content-type', 'application/json')
    try:
        with urllib.request.urlopen(req, data=data, timeout=20) as resp:
            raw = resp.read()
            status = resp.status
            response_headers = {k.lower(): v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
        response_headers = {k.lower(): v for k, v in exc.headers.items()}
    try:
        payload = json.loads(raw.decode() or '{}')
    except Exception:
        payload = raw.decode(errors='replace')[:1200]
    return status, response_headers, payload


def _redact_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        out = {}
        for key, value in payload.items():
            lk = str(key).lower()
            if lk in {'raw_payment_tokens_returned', 'raw_payment_proofs_returned', 'provider_api_keys_returned'}:
                out[key] = _redact_payload(value)
            elif any(s in lk for s in ('token', 'signature', 'authorization', 'secret', 'proof')) and lk not in {'payment_proof_hash'}:
                out[key] = '[REDACTED]'
            else:
                out[key] = _redact_payload(value)
        return out
    if isinstance(payload, list):
        return [_redact_payload(item) for item in payload[:20]]
    return payload


def _record(results: list[CheckResult], check_id: str, ok: bool, status: int | None, expected: str, detail: str, payload: Any = None) -> None:
    results.append(CheckResult(check_id, ok, status, expected, detail, _redact_payload(payload)))


def main() -> int:
    parser = argparse.ArgumentParser(description='DDG agent checkout conformance probe')
    parser.add_argument('--base-url', default='https://agents.daedalusdevelopmentgroup.com')
    parser.add_argument('--agent-id', default=f'conformance-probe-{int(time.time())}')
    parser.add_argument('--service-id', default='agent_checkout_conformance_audit')
    parser.add_argument('--target-url', default='https://example.com')
    parser.add_argument('--mock-payment-token', help='Dev/local only. Sends Payment-Signature with this token, e.g. mock-valid.')
    parser.add_argument('--mpp-credential', help='Real MPP credential. Sends Authorization: Payment <credential>.')
    parser.add_argument('--x402-signature', help='Real x402 credential. Sends Payment-Signature.')
    parser.add_argument('--direct-crypto-proof-json', help='Real direct-crypto proof JSON. Sends X-Direct-Crypto-Proof.')
    args = parser.parse_args()

    base = args.base_url.rstrip('/')
    order_path = f'{base}/v1/order-intake'
    body = {'service_id': args.service_id, 'target': {'url': args.target_url}, 'budget_usd': 35}
    results: list[CheckResult] = []

    status, _, payload = _request('POST', order_path, {}, body)
    _record(results, 'identity_gate', status == 403 and isinstance(payload, dict) and payload.get('error') == 'agent_only', status, '403 agent_only', 'missing agent id should be rejected before payment', payload)

    agent_headers = {'X-Agent-Id': args.agent_id, 'Idempotency-Key': f'{args.agent_id}-challenge'}
    status, _, payload = _request('POST', order_path, agent_headers, body)
    _record(results, 'payment_challenge', status in {402, 503}, status, '402 payment_required (or 503 if provider readiness gate is intentionally blocking)', 'agent id without payment should not create an order', payload)

    fake_headers = {'X-Agent-Id': args.agent_id, 'Idempotency-Key': f'{args.agent_id}-fake', 'Payment-Signature': 'invalid-fake-token'}
    status, _, payload = _request('POST', order_path, fake_headers, body)
    _record(results, 'fake_payment_fails_closed', status in {402, 503}, status, '402/503, never 2xx', 'invalid credential must fail closed', payload)

    paid_headers = {'X-Agent-Id': args.agent_id, 'Idempotency-Key': f'{args.agent_id}-paid'}
    if args.mock_payment_token:
        paid_headers['Payment-Signature'] = args.mock_payment_token
    if args.x402_signature:
        paid_headers['Payment-Signature'] = args.x402_signature
    if args.mpp_credential:
        paid_headers['Authorization'] = f'Payment {args.mpp_credential}'
    if args.direct_crypto_proof_json:
        paid_headers['X-Direct-Crypto-Proof'] = args.direct_crypto_proof_json

    order_id = None
    if any(k in paid_headers for k in ('Payment-Signature', 'Authorization', 'X-Direct-Crypto-Proof')):
        status, headers, payload = _request('POST', order_path, paid_headers, body)
        ok = status == 202 and isinstance(payload, dict) and all(payload.get(k) for k in ('order_id', 'status_url', 'artifact_url', 'receipt_console_url'))
        _record(results, 'accepted_order_returns_console_links', ok, status, '202 with order_id/status_url/artifact_url/receipt_console_url', 'paid/dev-paid order should queue and expose agent-readable console links', payload)
        if isinstance(payload, dict):
            order_id = payload.get('order_id')

        status2, headers2, payload2 = _request('POST', order_path, paid_headers, body)
        _record(results, 'idempotency_replay_same_body', status2 == status and headers2.get('x-idempotent-replay') == 'true', status2, 'same status + x-idempotent-replay:true', 'same body/idempotency key should replay cached success', payload2)

        changed = dict(body)
        changed['budget_usd'] = 36
        status3, _, payload3 = _request('POST', order_path, paid_headers, changed)
        _record(results, 'idempotency_conflict_changed_body', status3 == 409, status3, '409 idempotency_conflict', 'same key with changed body after cached success should conflict', payload3)
    else:
        _record(results, 'accepted_order_returns_console_links', True, None, 'skipped without credential', 'pass --mock-payment-token for local/dev full-path test or real credential args for a spending test')

    if order_id:
        status, _, payload = _request('GET', f'{base}/v1/orders/{order_id}', {'X-Agent-Id': args.agent_id})
        _record(results, 'order_status_same_agent', status == 200 and isinstance(payload, dict) and payload.get('order_id') == order_id, status, '200 same order id', 'same agent identity can retrieve redacted status', payload)

        status, _, payload = _request('GET', f'{base}/v1/orders/{order_id}', {'X-Agent-Id': args.agent_id + '-other'})
        _record(results, 'order_status_other_agent_forbidden', status == 403, status, '403', 'different agent identity cannot retrieve order status', payload)

        status, _, payload = _request('GET', f'{base}/v1/orders/{order_id}/artifact', {'X-Agent-Id': args.agent_id})
        _record(results, 'order_artifact_pending_or_ready', status in {200, 202}, status, '200 or 202', 'artifact endpoint should be stable before and after fulfillment', payload)

    report = {'ok': all(r.ok for r in results), 'base_url': base, 'agent_id': args.agent_id, 'checks': [asdict(r) for r in results]}
    print(json.dumps(report, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
