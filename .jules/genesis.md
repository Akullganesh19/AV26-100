## 2026-07-26 — API Retry Mechanism

**Failure point found:** External API calls (Weather API, Algolia, SendGrid, Cloudinary) lacked transient failure handling and retry mechanisms.
**Why it existed:** The `WeatherClient` in `integrations.py` only used standard requests without robust backoff, leaving the ingestion pipeline vulnerable to silent or cascading failures on timeouts or 5xx errors from the third-party service. `IntegrationService` methods offloaded to threads but also lacked retry protection.
**Recovery built:** Extracted `WeatherClient` properly into `integrations.py` and built a robust `with_retry` exponential backoff mechanism in `app.core.utils.py` and wrapped vulnerable async/sync outbound network calls (`httpx.get`, `algoliasearch`, `SendGrid`, `Cloudinary`).
**Blast radius before:** Any transient API failure would fail the entire daily pipeline run, potentially stalling alert creation or failing to send critical notifications.
**Watch for:** Other integrations or synchronous I/O blocks lacking `with_retry` + `asyncio.to_thread`.
