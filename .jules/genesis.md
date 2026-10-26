## 2024-10-26 — Auto-Retry Mechanics and Task Retention
**Failure point found:** External third-party integrations (Algolia) failed silently on transient errors, and background tasks were prone to garbage collection mid-execution.
**Why it existed:** Lack of systematic backoff utility and misunderstanding of asyncio task lifecycle.
**Recovery built:** Created `with_retry` utilizing exponential backoff and `inspect.isawaitable()`. Added task retention sets to prevent silent GC destruction. Applied retries to Algolia integration.
**Blast radius before:** Silent failure to sync data, and silent death of background tasks.
**Watch for:** Other integrations lacking retry mechanisms.
