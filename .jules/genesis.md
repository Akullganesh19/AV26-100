## 2024-08-24 — Resilient External Integrations & Reliable Background Tasks
**Failure point found:** External API calls to Algolia, SendGrid, and Cloudinary lacked retry logic, meaning a single transient network error would cause the operation to fail silently. Additionally, background tasks dispatched via `asyncio.create_task` were missing strong references, risking premature garbage collection mid-execution.
**Why it existed:** Developers likely assumed external services were always available and misunderstood `asyncio`'s garbage collection behavior for unawaited background tasks.
**Recovery built:** Wrapped external integration calls with a robust `with_retry` utility offering exponential backoff. Implemented a strong reference mechanism (`_background_tasks` set) for `asyncio` background tasks to ensure they run to completion.
**Blast radius before:** 100% of integration calls were susceptible to silent failure on network blips. High-priority alerts could silently disappear without notifying health officials.
**Watch for:** Other areas using `asyncio.create_task` or making external network requests without the `with_retry` wrapper.
