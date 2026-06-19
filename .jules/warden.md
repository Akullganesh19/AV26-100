## 2024-05-24 — API Error Response PII Leak
**Data traced:** Stack traces and internal error strings containing potentially sensitive internal states or PII depending on the exception.
**Exposure found:** `backend/app/api/routes/districts.py`, `backend/app/api/routes/predict.py`, and `backend/app/api/routes/clinical.py` endpoints were raising HTTPExceptions with `detail=str(e)` and sometimes logging `str(e)` explicitly in database audit records, passing raw error structures back to the client and database.
**Fix:** Redacted `str(e)` from being returned to the client and logged to DB by replacing it with a generic `"Internal server error"` string, and ensured the real exception is logged properly internally via `logger.error("...", exc_info=True)`.
**Coverage confirmed:** The `districts.py`, `predict.py`, and `clinical.py` API endpoints no longer use `str(e)` in any exception handler responses or audit logs.
**Still exposed elsewhere:** There might be other error handling routines (like global error handlers or middleware) that may inadvertently expose PII; we only targeted the explicitly identified endpoints.

## 2024-05-24 — Added Global Exception Handler
**Data traced:** Global exceptions
**Exposure found:** If an unhandled exception reached the global layer, FastAPI would normally wrap it in an `Internal Server Error` but sometimes could bubble up or error handling might log details locally based on other settings. Structural gap is lack of a unified global catch-all logging mechanism for internal server errors that ensures PII does not leak if custom handlers are misconfigured.
**Fix:** Created a structural global `Exception` handler in `backend/app/main.py` that catches all unhandled `Exception`s, logs `logger.error("Unhandled exception caught", exc_info=True)`, and returns a clean `500 Internal server error` `JSONResponse`.
**Coverage confirmed:** Tested through backend tests to ensure the application starts and that global routes correctly operate without breakage.
**Still exposed elsewhere:** This is a safety net; specific API routes explicitly catching and re-raising should ideally be cleaned up eventually, but are currently handled explicitly as well.
