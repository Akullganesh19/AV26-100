## 2024-05-27 — Fix Active PII and System Internal Leakage

**Data traced:** User Email Addresses and Internal System Exception Traces (`str(e)`)
**Exposure found:** Plaintext API error responses leaking infrastructure errors (`HTTPException` with `str(e)`) and unredacted PII in server logs.
**Fix:** Masked emails (`u***@domain.com`) structurally at the logging tier via `structlog` (`redact_pii_processor`), explicitly linking it to standard `logging`. Replaced raw `str(e)` in HTTP endpoints with generic errors and `logger.exception()`.
**Coverage confirmed:** The `redact_pii_processor` avoids cyclic structures and recursively checks dicts/lists. Confirmed backend test suite passes and logging stack correctly formats traces.
**Still exposed elsewhere:** Audit logs currently rely on hashing inputs (which prevents raw plaintext exposure, but is vulnerable to dictionary attacks if the salt is weak or absent), which should be reviewed in the future.
## 2024-05-27 — Fix CI Test Conftest Leakage

**Data traced:** CI Database Credentials
**Exposure found:** The CI workflow supplies `DATABASE_URL` ending in `_test`. But `conftest.py` appended `_test` indiscriminately, resulting in a connection attempt to `episense_test_test` which caused test suites to crash.
**Fix:** Checked if `TEST_DATABASE_URL` ends with `_test` before appending it.
**Coverage confirmed:** The test suite now passes locally.
**Still exposed elsewhere:** N/A for this fix.
