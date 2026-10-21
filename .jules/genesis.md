## 2024-10-21 — Auto-Retry for Third-Party Integration API Calls
**Failure point found:** External API calls to Algolia, SendGrid, and Cloudinary within IntegrationService lacked any retry logic or fallback handling.
**Why it existed:** Initially written with standard asyncio.to_thread offloading to unblock the event loop but did not account for network latency or transient provider outages.
**Recovery built:** Implemented a robust `with_retry` wrapper in `app.core.resilience` supporting both sync and async execution with exponential backoff.
**Blast radius before:** Any transient API failure led to missing reports, dropped critical health alerts, or out-of-sync search indexes with no automatic recovery.
**Watch for:** Similar unprotected third-party integrations throughout the app, especially missing retry mechanisms in background task processors like `alert_service.py` or Celery queues.
