## 2024-05-24 — [Added Resilient Integration Service]
**Failure point found:** Unprotected third-party API calls in IntegrationService (Algolia, SendGrid, Cloudinary) that lacked retry logic, circuit breakers, and idempotency guards.
**Why it existed:** The app was built assuming a happy-path network, with no safety nets for transient 500s or timeouts.
**Recovery built:** Added exponential backoff retries, circuit breakers, and idempotency guards to IntegrationService.
**Blast radius before:** Silent background task failures, missing emails, and failed uploads without any recovery, impacting all asynchronous notification and syncing flows.
**Watch for:** Other external HTTP clients or DB calls that lack the same resilience layers.
