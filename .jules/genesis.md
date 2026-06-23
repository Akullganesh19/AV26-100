## 2026-06-23 — Third-Party Integration Resilience
**Failure point found:** External calls to Algolia, SendGrid, and Cloudinary in IntegrationService had no retry logic or circuit breakers. A transient failure would propagate upwards, potentially breaking workflows (e.g. failing to send a critical health alert).
**Why it existed:** The integrations were implemented with direct API calls without a resilience wrapper, likely to get MVP out faster.
**Recovery built:** Added `@with_retry` and `@with_circuit_breaker` decorators to the methods in IntegrationService.
**Blast radius before:** Any network blip or third-party API outage would result in a hard failure, causing silent failures in background tasks or 500 errors in user-facing APIs.
**Watch for:** Other direct external API calls without resilience, especially in ingestion services.
