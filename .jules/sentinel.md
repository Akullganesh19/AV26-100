## 2024-07-03 — Information Leakage in Error Handlers
**Found:** Broad `except Exception` blocks catching application/infrastructure errors and passing `str(e)` directly into the `detail` parameter of FastAPI `HTTPException`.
**Why it existed:** Quick implementation for surfacing error context back to the frontend/client for debugging during early development.
**Fix:** Modified error handlers in `main.py`, `clinical.py`, `districts.py`, and `predict.py` to log the full exception (`exc_info=True`) internally while returning a sanitized, static generic error message to the client.
**Learning:** Always separate internal diagnostic logs from external client-facing errors. Leaking `str(e)` can inadvertently reveal infrastructure details, SQL queries, or third-party service topologies.
**Watch for:** New endpoints or background tasks using `HTTPException` with dynamic content.
