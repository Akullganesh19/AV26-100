## 2026-07-07 — Fix structural logging redaction and client error leakage
**Data traced:** PII (email, password, clerk_id, tokens) and system internals (exception traces).
**Exposure found:** PII was logged unredacted via standard application logging. Exception `str(e)` messages (which contain stack traces, invalid values, and schema details) were leaked directly to users in HTTP 500 error responses and stored in DB audit logs.
**Fix:** Implemented a robust `redact_pii_processor` in `backend/app/core/logging.py` wrapping both `structlog` and standard logging. Stripped `str(e)` details from all client-facing HTTP exceptions, replacing them with generic errors and internal logs using `logger.exception`. Updated `PredictionAuditLog` to store exception types instead of raw traces.
**Coverage confirmed:** Tested exception handling and structured logging configs. The redaction logic masks emails and fully blanks out passwords, IDs, and tokens without corrupting nested data structures or triggering recursion limits.
**Still exposed elsewhere:** The current fixes do not audit or verify data deletion paths across third-party tools (SendGrid, Algolia, StreamChat).
