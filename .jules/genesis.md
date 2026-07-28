## 2026-07-28 — Unprotected External API Calls in Integrations
**Failure point found:** Sync I/O operations (`cloudinary.uploader.upload`, `sg.send`, `index.save_object`) in `IntegrationService` lacked retry mechanisms, and Cloudinary upload was blocking the async event loop.
**Why it existed:** Initially written for happy-path operations without considering network transience or resilience of third-party API dependencies.
**Recovery built:** Created an asynchronous `with_retry` decorator utilizing exponential backoff and `asyncio.sleep` to wrap outgoing API calls. Shifted `cloudinary.uploader.upload` to run safely in `asyncio.to_thread`.
**Blast radius before:** A single network blip or 503 from Algolia/Sendgrid/Cloudinary would completely fail the user transaction with no fallback or retry.
**Watch for:** Other integrations or synchronous I/O operations in services acting as transient network dependencies.
