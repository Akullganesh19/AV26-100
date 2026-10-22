## 2024-10-22 — Third-Party API Integration Resiliency
**Failure point found:** Algolia, Sendgrid, and Cloudinary APIs in `IntegrationService` had no retry mechanisms and would hard-fail on transient network issues.
**Why it existed:** I/O operations were offloaded to threads but lacked exponential backoff wrappers.
**Recovery built:** Wrapped all outbound third-party calls in `backend/app/api/integrations.py` with `with_retry` and exponential backoff.
**Blast radius before:** High - any momentary DNS blip or 503 from a third-party would break critical flows like alert dispatch or search indexing silently or with raw errors.
**Watch for:** Other outbound HTTP integrations (like webhook receivers or the mocked `weather_client`) missing similar wrappers.
