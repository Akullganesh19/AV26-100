## 2024-07-29 — Unprotected External APIs (Algolia, SendGrid, Cloudinary)

**Failure point found:** Algolia, SendGrid, and Cloudinary APIs were called synchronously and without any retry or backoff mechanism inside `IntegrationService`.
**Why it existed:** The integration service was built prioritizing functionality over resilience, assuming external APIs are always available and fast.
**Recovery built:** Implemented an asynchronous `with_retry` wrapper that retries operations up to 3 times with exponential backoff.
**Blast radius before:** Any transient network issue or third-party outage would cause the calling function to fail immediately, leading to missed alerts, failed syncs, or broken uploads, potentially affecting critical alerting workflows.
**Watch for:** Other external API dependencies (like `WeatherClient` or future external webhooks) that lack retry logic or execute blocking I/O on the main event loop.
