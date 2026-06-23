# Security Policy

Report security issues to `0xcircuitbreaker@protonmail.com`.

Please do not send secrets in issue bodies, service targets, or public pull requests. If you need to provide sensitive evidence, send a minimal redacted reproducer first.

## DDG public security boundaries

- Public agents call only `https://agents.daedalusdevelopmentgroup.com`.
- Verifier sidecars are private and are not public API endpoints.
- MPP is not live until a real penny settlement proof passes.
- DDG returns redacted receipts/artifacts and avoids buyer contact leakage.
- Dynamic execution/browser/security scans are sandboxed or operator-reviewed.
