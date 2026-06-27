## 2024-07-29 — Unprotected Third-Party External Calls
**Failure point found:** External calls in `IntegrationService` (Algolia, SendGrid, Cloudinary) lacked retry and fallback protections.
**Why it existed:** The service was built to integrate with APIs but did not account for transient network failures or third-party outages.
**Recovery built:** Added `@with_retry` (exponential backoff) and `@with_circuit_breaker` decorators to methods offloading to third-party APIs.
**Blast radius before:** Any temporary hiccup in SendGrid, Algolia, or Cloudinary could cause critical alert failures, lost report uploads, or out-of-sync searches, directly impacting users.
**Watch for:** Other external dependencies that use plain `asyncio.to_thread` or synchronous HTTP calls without similar resilience wrapping.
