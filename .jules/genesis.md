## 2024-08-02 — [Auto-Retry and Graceful Degradation for Third-Party Integrations]
**Failure point found:** Third-party integrations in `backend/app/api/integrations.py` (Algolia, SendGrid, Cloudinary) were completely unprotected. Any transient network failure or remote 500 error would crash the asynchronous loop or main execution flow.
**Why it existed:** Historically, external APIs were assumed to be 100% reliable, leading to naked I/O calls being offloaded to threads without resiliency mechanisms.
**Recovery built:** Created an asynchronous `with_retry` utility supporting exponential backoff. Applied it to Algolia and Cloudinary synchronizations. Added standard `try/except` graceful degradation to SendGrid to prevent double-emailing (non-idempotent) while still protecting the primary application flow.
**Blast radius before:** Any external CDN or search indexing glitch would cascade, taking down core application functions like report generation or district creation.
**Watch for:** Other unpatched asynchronous background tasks or naked API calls across worker processes that may require similar wrapping.
