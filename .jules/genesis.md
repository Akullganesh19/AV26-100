## 2024-10-16 — External Network Calls & Async Task Vulnerabilities
**Failure point found:** External integrations (Algolia, SendGrid, Cloudinary) in `IntegrationService` had no retry logic on network failures. Async background tasks (`asyncio.create_task`) in `PredictionService` were launched fire-and-forget without a strong reference, risking silent destruction by garbage collection.
**Why it existed:** Happy-path implementation without considering transient network failures or Python's `asyncio` GC mechanics.
**Recovery built:** Created `with_retry` exponential backoff mechanism in `app.core.resilience` and wrapped all external I/O calls. Added a module-level `background_tasks` set to protect background alert dispatch tasks from garbage collection.
**Blast radius before:** Transient 500s or timeouts from SendGrid/Algolia would cause silent failure or dropped alerts. Alert tasks could be silently killed mid-execution.
**Watch for:** Other `asyncio.create_task` instances lacking strong references, and synchronous third-party SDK calls blocking the event loop or missing retry guards.
