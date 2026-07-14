## 2024-07-14 — Critical Task and Async I/O Resilience Improvements
**Failure point found:**
1. `IntegrationService` methods calling Algolia, SendGrid, and Cloudinary had no retry logic, failing permanently on transient errors (like 503 or network timeouts). Moreover, `cloudinary.uploader.upload` was blocking the async event loop.
2. In `PredictionService`, `send_alert_notification` was dispatched using `asyncio.create_task` without retaining a reference, exposing the task to premature destruction by Python's Garbage Collector.

**Why it existed:**
1. Lack of robust asynchronous task orchestration and resilience patterns when originally integrating third-party libraries.
2. Direct usage of `asyncio.create_task` as a "fire-and-forget" mechanism is a common async Python pitfall when developers forget that background tasks need strong references to stay alive.

**Recovery built:**
1. Introduced a `with_retry` utility with exponential backoff and logging for external IO operations.
2. Refactored `IntegrationService` to wrap synchronous and asynchronous external calls using `with_retry` and `asyncio.to_thread` for the synchronous Cloudinary call.
3. Tracked background task dispatch in `PredictionService` using a module-level `_background_tasks` set, preventing silent garbage collection destruction of critical alert tasks.

**Blast radius before:**
1. External integration timeouts could halt report generation, alert dispatches, and search syncing.
2. Garbage collection of critical alerts meant high risk outbreak warnings could be silently dropped with zero indication.

**Watch for:**
1. Similar synchronous calls in other async contexts.
2. "Fire-and-forget" `asyncio.create_task` uses elsewhere in the codebase.
