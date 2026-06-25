## 2025-02-23 — Prevent Clinical PII Leak in Database Audit Logs
**Data traced:** Clinical screening data (e.g., age, insulin, blood pressure).
**Exposure found:** Plaintext clinical data was leaked via `str(e)` inside the `metadata_json` field of `PredictionAuditLog` when a validation error or processing exception occurred during screening.
**Fix:** Updated the `diagnose_heart`, `diagnose_diabetes`, and `diagnose_parkinsons` endpoints to extract the exception class name (`e.__class__.__name__`) rather than the full raw string representation of the exception, preventing raw validation data from being logged to the database.
**Coverage confirmed:** Manually triggered error paths and verified through code review that `log_prediction` receives the sanitized class name instead of raw exception string. Validated endpoints logic. Tests continue to pass.
**Still exposed elsewhere:** There may be other areas where Pydantic `ValidationError` raw string traces leak PII if not caught appropriately (e.g., in default FastAPI exception handlers or infrastructure logging). No deletion path exists yet for old logs.
