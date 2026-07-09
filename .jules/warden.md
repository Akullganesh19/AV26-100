## 2026-07-09 — Close Logging PII Exposure
**Data traced:** User emails, passwords, clerk_ids, and clinical metrics.
**Exposure found:** Plaintext leakage into application logs whenever passed via `extra={}` kwargs or structlog dictionaries.
**Fix:** Created and injected a recursive structlog processor (`redact_pii_processor`) to irreversibly mask or redact specific keys. Configured standard Python logging to route through structlog to ensure system-wide coverage.
**Coverage confirmed:** Verified via autonomous test scripts that standard logging calls with sensitive `extra` parameters successfully output `[REDACTED]` or partially masked strings (`h***@example.com`) without causing infinite loops or modifying the underlying application memory state.
**Still exposed elsewhere:** While logging is secured, other boundaries (e.g. data leaving the system to SendGrid or external analytic services) might still require deep field-level redaction, and a comprehensive mechanism for user data deletion is still lacking.
