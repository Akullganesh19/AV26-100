## 2023-10-26 — Self-Healing Integrations and Background Tasks
**Failure point found:** Fire-and-forget background tasks for alerts lacked strong references (silent GC dropping) and external integrations (Algolia, SendGrid, Cloudinary) lacked transient failure retries.
**Why it existed:** Tasks spawned asynchronously were not kept in a reference list, and standard library I/O offloading lacked exponential backoff wrappers.
**Recovery built:** Implemented `with_retry` utility supporting async/sync tasks and added a strong reference module-level `set()` for alert tasks.
**Blast radius before:** Silent failure of mission-critical outbreak alerts to officials; brittle external data sync.
**Watch for:** Other `asyncio.create_task` calls lacking references and other raw API calls lacking backoff.
