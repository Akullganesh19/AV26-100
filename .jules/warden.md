## 2026-07-06 — PII Redaction in Logging

**Data traced:** PII fields including `email`, `password`, `ssn`, `phone` in standard logs.
**Exposure found:** PII like user email addresses were passing in plaintext through `structlog` events and `logging` extra payloads (via JSON logging or stdout), making them visible to anyone with access to observability platforms, Docker console, or text logs.
**Fix:** Created a recursive `redact_pii_processor` in `backend/app/core/logging.py` that strips out PII fields or partially masks emails dynamically, handling deep dicts and lists safely while preventing infinite loops on cyclic references.
**Coverage confirmed:** Intercepted logs directly going through both `structlog` events and Python's standard `logging` using `extra=`. Tested cycle resolution (`self` references) and confirmed structural outputs remained intact while emails were masked (e.g. `j***@episense.gov`).
**Still exposed elsewhere:** Currently, password reset tokens and detailed prediction inputs (`input_hash`) are logged, though partially hashed, may contain reversible data if `predict` logging payload captures `data.dict()` entirely.
