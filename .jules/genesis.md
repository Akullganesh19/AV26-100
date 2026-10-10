## 2026-10-10 — Resilient API Integrations & Safe Background Tasks
**Failure point found:** Sync I/O blocking event loop and no retry protection on Algolia/SendGrid/Cloudinary API calls. Background tasks in PredictionService vulnerable to silent garbage collection.
**Why it existed:** Assumed fast network and external APIs always succeed; missed asyncio object lifetime and reference holding best practices.
**Recovery built:** Created `with_retry` wrapper. Wrapped third-party calls in `asyncio.to_thread` protected with exponential backoff. Retained background tasks in a strong module-level set.
**Blast radius before:** 3rd-party outage crashes current requests (silent failures) or hangs the event loop. In-flight alert tasks disappear unpredictably.
**Watch for:** Other integrations with missing network retry or any other unprotected `asyncio.create_task`.
