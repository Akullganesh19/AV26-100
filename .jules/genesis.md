## 2024-10-15 — [Task GC Bug & API Retry Protection]
**Failure point found:** Fire-and-forget background tasks (e.g. `asyncio.create_task`) lacked strong references, making them prone to silent GC cancellation. External integrations (Algolia, SendGrid) lacked retry logic on transient HTTP errors.
**Why it existed:** Native `asyncio.create_task` design can silently drop tasks when unreferenced. API clients were assumed to be perfectly reliable.
**Recovery built:** Implemented `background_tasks = set()` with `add_done_callback` to hold references until completion. Wrapped Algolia and SendGrid external calls in an exponential backoff `with_retry` wrapper.
**Blast radius before:** Silent dropping of alerts, silent failures to sync search districts or send health emails.
**Watch for:** Other fire-and-forget tasks or synchronous I/O operations without retries or without holding references.
