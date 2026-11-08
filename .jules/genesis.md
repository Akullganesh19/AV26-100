## 2024-11-08 — Unprotected Integrations and Silent Task Deaths
**Failure point found:** External integrations (Algolia, SendGrid, Cloudinary) were lacking retry logic and timeout protection. Fire-and-forget background tasks for sending alerts were susceptible to premature garbage collection.
**Why it existed:** Assumed happy paths for 3rd-party APIs and naive `asyncio.create_task` usage without retaining references.
**Recovery built:** Added an async `with_retry` wrapper with exponential backoff for external service calls. Maintained strong references to background tasks to prevent GC. Fixed a blocking sync call in Cloudinary upload by properly using `asyncio.to_thread`.
**Blast radius before:** Silent dropping of alerts and search indexing failures upon transient API errors or heavy load. Blocking event loop during Cloudinary uploads degrading overall app performance.
**Watch for:** Other `asyncio.create_task` calls or un-offloaded sync I/O calls in third-party integrations.
