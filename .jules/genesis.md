## 2024-05-24 — API Integrations Resilience

**Failure point found:** External API integrations (Algolia, SendGrid, Cloudinary) were completely unprotected. Any transient network failure or remote API 500 would crash the calling backend flow silently or loudly without any retries.
**Why it existed:** Initially built as happy-path only logic to unblock features quickly.
**Recovery built:** Created an asynchronous `with_retry` utility supporting exponential backoff (0.1s, 0.2s, 0.4s). Integrated this into all outbound SDK calls within `IntegrationService`, wrapping the `asyncio.to_thread` execution. Also added graceful degradation for Algolia and Cloudinary (returning `None` on failure) so the primary transaction doesn't fail just because an auxiliary service is down.
**Blast radius before:** Any temporary SendGrid or Cloudinary hiccup would break alert dispatch and report generation respectively. Algolia timeouts would break district updates.
**Watch for:** Other spots in the codebase that use external SDKs (like `weather_client`) that may need similar wrapping.
