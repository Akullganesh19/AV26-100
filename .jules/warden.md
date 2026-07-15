## 2026-07-15 — PII Leak in Logging Extra Keyword Arguments
**Data traced:** User PII including `email`, `password`, `ssn`, `phone`, `address`, `dob`, `date_of_birth`, `card_number`.
**Exposure found:** Standard library logging was being used and dictionary fields injected via the `extra` kwarg would log PII fields directly to standard output (and subsequently, log management solutions) without any form of redaction.
**Fix:** Refactored `backend/app/core/logging.py` to pipe standard library logging through `structlog.stdlib.ProcessorFormatter` and implemented a global recursive `redact_pii_processor`. Emails are partially masked (e.g. `j***@gmail.com`) and other sensitive fields are replaced with `[REDACTED]`. Added cyclic reference protection to prevent deep-traversal crashes.
**Coverage confirmed:** Created a Python test script (`backend/test_log.py`) and ran it to confirm that dictionaries containing PII fields (even within lists or tuples) are successfully redacted before JSON serialization, and that recursive data structures do not cause crashes.
**Still exposed elsewhere:** Potential leaks through frontend analytics/tracking tools or other untracked external sinks.
