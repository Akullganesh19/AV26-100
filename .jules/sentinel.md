## 2024-07-08 — System Information Leakage in Error Responses
**Found:** Raw exception strings (`str(e)`) were being returned directly to users in HTTP 500 error responses across several critical API endpoints (`main.py`, `clinical.py`, `predict.py`, `districts.py`).
**Why it existed:** Developers often use `str(e)` in development to quickly identify issues without checking logs, which accidentally gets carried over into production environments.
**Fix:** Replaced `str(e)` in `HTTPException` details with generic error messages (e.g., "An internal error occurred"). Logged the actual exceptions securely on the server-side using `logger.exception()`. In `log_prediction`, used `type(e).__name__` instead of `str(e)` to record the error type without leaking internals.
**Learning:** Always decouple user-facing error messages from internal system state. `str(e)` should never cross the API boundary, as it can leak stack traces, database schema details, or file paths.
**Watch for:** New endpoints or background task failure handlers being added that simply wrap `try/except Exception as e` and return or persist `str(e)` to client-accessible records.
