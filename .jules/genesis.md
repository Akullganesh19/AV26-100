## 2024-05-24 — [Resilience for Third-Party Integrations and Background Tasks]
**Failure point found:** External API calls (Algolia, SendGrid, Cloudinary) lacking transient error handling; background alert tasks silently being killed by garbage collection.
**Why it existed:** Assumed happy path for 3rd party services; overlooked asyncio strong reference requirement for background tasks.
**Recovery built:** Added `with_retry` function providing auto-retry with exponential backoff for integrations. Stored background tasks in a strong reference `set()`. Wrapped blocking Cloudinary call in `asyncio.to_thread`.
**Blast radius before:** Silent failure in district search syncing, alert emails failing silently due to network blips, alert notifications completely un-dispatched due to GC, blocking event loop on report upload.
**Watch for:** Other `asyncio.create_task` fire-and-forget patterns and missing retry logic around database connection faults or third-party webhooks.