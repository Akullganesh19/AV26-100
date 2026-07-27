## 2024-03-22 — [Logging PII Exposure Fix]
**Data traced:** Email, password, password_hash, clerk_id, phone, ssn, address, dob, card_number, token, access_token
**Exposure found:** `extra={}` in Python `logging` or direct structlog calls could expose plaintext PII in JSON application logs. Standard Python `logging` was not fully integrated with `structlog` meaning `extra={}` arguments would bypass redaction or logging handlers, risking PII exposure.
**Fix:** Created `redact_pii_processor` in `backend/app/core/logging.py`, safely handling cyclic references and deeply nested arrays/dictionaries. Standardized logging so both `logging` and `structlog` pass through the JSON and redaction processor.
**Coverage confirmed:** Tested standalone script verifying nested PII removal, cyclic structure protection, and email context preservation (`j***@example.com`). Both standard `logging.getLogger` and `structlog.get_logger` are fully covered.
**Still exposed elsewhere:** Audit logs still hash inputs which might contain predictable data depending on usage. Need to ensure error payloads to frontend are not leaking PII, but log layer is secured.
