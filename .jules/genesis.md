## 2024-10-19 — Added Resilience Mechanisms
**Failure point found:** Third-party APIs (Algolia, SendGrid, Cloudinary) lacked retries; background alert tasks were unreferenced and susceptible to GC; alert dispatch failures were silently ignored.
**Why it existed:** Quick implementation of synchronous/async API clients without wrapping in resilience layers or correctly handling background tasks and failures.
**Recovery built:** Added `with_retry` for transient API failures; protected `asyncio.create_task` with strong references; implemented a Redis DLQ (`dead-letter`) for alerts that permanently fail dispatch.
**Blast radius before:** Silent failure of notifications, search index sync, and report uploads; intermittent loss of critical outbreak alerts affecting users directly.
**Watch for:** Other unreferenced `asyncio.create_task` usage and direct third-party SDK calls missing `with_retry`.
