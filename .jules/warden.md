## 2026-06-29 — PII Leak in Standard Error/Info Logs
**Data traced:** PII (email, password, ssn, clerk_id)
**Exposure found:** Plaintext standard library logging in application APIs (via extra dictionaries) and direct string embedding in log messages.
**Fix:** Created `redact_pii_processor` in `backend/app/core/logging.py` that intercepts all `structlog` output. Explicitly hooked standard library `logging` into structlog's formatter stream. It masks sensitive dict keys and regex-matches email addresses embedded directly in log text.
**Coverage confirmed:** Tested directly via Python scripts; log entries with `email`, `password`, `ssn`, `clerk_id` are redacted as `[REDACTED]`, and embedded emails in messages appear masked like `j***@gmail.com`. Checked against the Pytest test suite to ensure structural modifications did not introduce regression.
**Still exposed elsewhere:** This does not apply frontend-side telemetry or logs, meaning client-side console logs could still leak if not handled. Redaction also misses names, phone numbers, or DOB if those were explicitly embedded in free text.
