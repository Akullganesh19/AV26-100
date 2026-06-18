## 2026-06-18 — Exception Leakage Mitigation
**Data traced:** Stack traces and internal Exception states
**Exposure found:** Returned in API error details to the client during prediction, district data fetching, and PDF report generation.
**Fix:** Modified error handlers in `clinical.py`, `predict.py`, and `districts.py` to log errors internally using `logger.error(..., exc_info=True)` and return generic HTTP 500 error messages to the client.
**Coverage confirmed:** Reviewed the trace of `HTTPException` and `except Exception` and verified the fix was applied to the highest exposure paths. Also ran `pytest` on backend tests to ensure it passes.
**Still exposed elsewhere:** Other endpoints may still leak internal errors, further auditing is required.
