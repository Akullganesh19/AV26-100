## 2024-07-03 — Information Leakage in Error Handlers
**Found:** Broad `except Exception` blocks catching application/infrastructure errors and passing `str(e)` directly into the `detail` parameter of FastAPI `HTTPException`.
**Why it existed:** Quick implementation for surfacing error context back to the frontend/client for debugging during early development.
**Fix:** Modified error handlers in `main.py`, `clinical.py`, `districts.py`, and `predict.py` to log the full exception (`exc_info=True`) internally while returning a sanitized, static generic error message to the client.
**Learning:** Always separate internal diagnostic logs from external client-facing errors. Leaking `str(e)` can inadvertently reveal infrastructure details, SQL queries, or third-party service topologies.
**Watch for:** New endpoints or background tasks using `HTTPException` with dynamic content.

## 2024-07-03 — CI Database URL Logic
**Found:** `conftest.py` appended `_test` to `DATABASE_URL` unconditionally, breaking CI runs where `DATABASE_URL` was already configured with `_test`.
**Why it existed:** Designed for local development where developers run against a primary database.
**Fix:** Added a conditional check `not str(settings.DATABASE_URL).endswith("_test")` before appending `_test`.
**Learning:** CI configurations frequently diverge from local development patterns. Database tests should be idempotent across environments.
**Watch for:** Similar hardcoded string modifications that break when environment variables already account for the expected state.
