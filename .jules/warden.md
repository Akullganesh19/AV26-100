## 2025-02-14 — Structural Redaction and Safe Exception Handling
**Data traced:** User identifiers (email, clerk_id, tokens), stack traces leaking exact internal values.
**Exposure found:** Exceptions via HTTP responses and error logs leaking exact database error strings and potentially full user data.
**Fix:** Masked email addresses and exact keys structurally using a `structlog` custom processor. Replaced `str(e)` in error handlers with `type(e).__name__` for DB logging and generic strings for API errors.
**Coverage confirmed:** Reviewed `backend/app/core/logging.py`, API endpoints, background services, and background tasks.
**Still exposed elsewhere:** Third party services like GetStream or Cloudinary may still accept and log sensitive district data unless sanitized prior to upload. Exports/CSV generation fields were not deeply audited this session.
