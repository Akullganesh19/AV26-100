## 2026-07-01 — Stop PII Leak in Logs
**Data traced:** PII (email, password, ssn, clerk_id, address, dob, date_of_birth, card_number, phone).
**Exposure found:** Standard library `logging` instances and uncaught print streams dumping sensitive raw PII directly into plaintext logs.
**Fix:** Refactored `backend/app/core/logging.py` to route all standard `logging` through `structlog`. Added a custom recursive `redact_pii_processor` to automatically intercept and mask sensitive keys and emails everywhere in event dictionaries before reaching JSON renderers.
**Coverage confirmed:** Wrote and successfully ran `backend/tests/test_logging.py` to verify recursive redaction works on dictionaries and explicit email regex substitutions work correctly for arbitrary strings.
**Still exposed elsewhere:** PII might still exist in non-deleted audit trails or specific unredacted system exception messages outside structured logger contexts.
