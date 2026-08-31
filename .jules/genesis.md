## 2024-06-03 — Protected External API Integrations
**Failure point found:** External API calls to SendGrid, Algolia, and Cloudinary in `IntegrationService` had no retry logic. Additionally, the Cloudinary upload was a blocking synchronous call in an async function.
**Why it existed:** MVP implementation optimized for happy-path delivery without considering third-party service degradation or transient network errors.
**Recovery built:** Added `with_retry` utility with exponential backoff (100ms base) and wrapped all external integration calls. Offloaded Cloudinary call to a separate thread.
**Blast radius before:** Any transient API failure would cause silent failures (Algolia sync) or loudly failing endpoints (Cloudinary report generation/SendGrid alerts), affecting end users.
**Watch for:** Other integrations or background jobs directly calling external services without idempotency or retry protections.
