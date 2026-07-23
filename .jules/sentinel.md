## 2025-02-12 — Information Leakage in API Exception Handlers
**Found:** Raw exception strings (`str(e)`) were being returned directly to the client in HTTP 500 error responses across multiple API endpoints (`main.py`, `districts.py`, `predict.py`, `clinical.py`).
**Why it existed:** A naive approach to error handling that aimed to provide debugging information to the client, failing to account for the security risks of exposing system internals.
**Fix:** Replaced the `detail` parameter in `HTTPException` with generic, user-safe error messages (e.g., "Internal Server Error"). Added internal logging via `logging.getLogger(__name__).error(..., exc_info=True)` to capture the actual exception details for developers.
**Learning:** Always verify that API endpoints do not leak stack traces or raw error messages. Fail securely by providing generic responses to the client while retaining detailed logs internally.
**Watch for:** New endpoints or exception handlers that might inadvertently expose sensitive context or system details.
