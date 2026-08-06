## 2024-08-06 — Resilient External Integrations
**Failure point found:** Sync I/O calls to Algolia, Cloudinary, and SendGrid inside `backend/app/api/integrations.py` were unprotected.
**Why it existed:** Quick implementation of external services without considering transient network failures or service outages.
**Recovery built:** Added exponential backoff retries via a custom `with_retry` wrapper. Implemented graceful degradation for non-critical services (Algolia, Cloudinary) to return `None` on ultimate failure. Added a Redis-backed idempotency guard for SendGrid to prevent duplicate email spam upon retry.
**Blast radius before:** A transient failure in a 3rd-party API would crash the entire request loop, affecting all users creating reports, saving districts, or triggering alerts.
**Watch for:** Other external HTTP requests or API clients that lack retry mechanisms or idempotency guards.