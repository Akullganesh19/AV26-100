## 2026-06-28 — PII Logging Exposure Closed
**Data traced:** PII Fields (Email, passwords, SSN, clerk_id, etc.)
**Exposure found:** Plaintext logs from python `logging` standard library and missing structlog key redaction.
**Fix:** Upgraded `backend/app/core/logging.py` to route all logs through `structlog` with a custom `redact_pii_processor` that masks sensitive keys and regexes out emails in log messages.
**Coverage confirmed:** Ran local tests confirming `logging.getLogger` and `structlog` both successfully redact PII without compromising JSON formatting.
**Still exposed elsewhere:** Audit logs database table (`audit_log.py`) and third-party integrations (`IntegrationService` email dispatch) could still be storing or sending PII.
