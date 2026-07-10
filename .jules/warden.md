## 2024-05-24 — Ensure PII is not leaked via structured application logging
**Data traced:** User emails (both direct parameters and nested structures)
**Exposure found:** `extra={...}` keyword arguments routed to unstructured or partially structured logging outputs, vulnerable to dumping complete PII configurations to central log aggregators.
**Fix:** Created `redact_pii_processor` in `backend/app/core/logging.py`, integrated standard library `logging` into `structlog` via `ProcessorFormatter`, correctly navigating deep dictionaries and detecting cyclic loops while partially masking email entries.
**Coverage confirmed:** The `redact_pii_processor` correctly ignores cycle references (`<cyclic>`), masks emails (`t***@example.com`), and handles non-string dictionary keys seamlessly during manual test scripting.
**Still exposed elsewhere:** Clinical integration payloads sent to SendGrid and streaming platforms are currently unredacted, but represent legitimate outbound pathways (not internal log leaks).
