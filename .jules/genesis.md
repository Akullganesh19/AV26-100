## 2026-07-30 — Transient External Failure Recovery (with_retry)
**Failure point found:** Unprotected third-party integrations (Algolia, SendGrid, Cloudinary) and external API fetching (WeatherClient in IngestionService) with no retry logic on transient network or API failures.
**Why it existed:** Initial implementation optimized for happy-path, assuming 100% uptime from external SaaS dependencies.
**Recovery built:** Added `with_retry` wrapper in `app.core.utils` with exponential backoff and applied it to vulnerable I/O operations (`IntegrationService` and `IngestionService`). Also tracked orphaned background tasks in `PredictionService` (`_background_tasks`).
**Blast radius before:** An API timeout from SendGrid, Algolia, Cloudinary, or Weather API would crash the request or background job, swallowing data or dropping critical alerts silently.
**Watch for:** Other external dependencies added later without backoff logic, and internal DB queries that might benefit from retry loops under high contention.
