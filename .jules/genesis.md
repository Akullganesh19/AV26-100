## 2026-10-07 — Added Resilience to Background Tasks and Third-Party API Calls
**Failure point found:** Background tasks using `asyncio.create_task` were unreferenced, risking silent termination by the garbage collector. Third-party API calls (`Algolia`, `SendGrid`, `Cloudinary`) were unprotected against transient failures.
**Why it existed:** The app relied on simplistic asynchronous spawning and naïve single-attempt integrations, likely optimized for speed over reliability.
**Recovery built:** Created `backend/app/core/resilience.py` with `safe_fire_and_forget` to hold strong references to background tasks and `with_retry` to add exponential backoff for external API calls. Refactored `prediction_service.py` and `integrations.py` to use these tools.
**Blast radius before:** If garbage collection kicked in mid-alert, critical notifications would fail silently. If a 3rd-party API briefly hiccupped, the operation permanently failed without fallback.
**Watch for:** Other fire-and-forget tasks or synchronous I/O operations lacking similar resilience wrappers.
