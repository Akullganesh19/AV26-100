## 2026-07-16 — Redact Sensitive User Fields in Logs
**Data traced:** PII/User Email Addresses (`email`, `emails` kwargs in standard logs)
**Exposure found:** System logs were capturing and printing raw standard library `extra={"email": "..."}` data without any redaction, presenting a massive active data leak.
**Fix:** Created `redact_pii_processor` in `backend/app/core/logging.py`. Masked emails recursively through JSON objects and lists. Removed bypass `logging.basicConfig` in config layer. Connected standard library to `structlog` using `ProcessorFormatter`.
**Coverage confirmed:** Tested nested emails inside logs structure recursively. Confirmed complete redaction without cyclic reference errors or JSON serialization failures.
**Still exposed elsewhere:** Potential PII exposure via analytics or 3rd party webhooks (requires next review session).
