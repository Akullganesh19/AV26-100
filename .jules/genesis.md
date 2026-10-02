## 2026-10-02 — Self-Healing Integrations and Background Tasks
**Failure point found:** Unprotected external I/O (Algolia, Sendgrid, Cloudinary) missing retry logic, and async tasks fire-and-forget without a strong reference leading to GC killing tasks.
**Why it existed:** Assumed happy-path network and standard fire-and-forget task patterns without considering garbage collector behaviors.
**Recovery built:** Added `with_retry` exponential backoff for external I/O and retained strong references for active background tasks.
**Blast radius before:** Silent task dropping and unhandled 5xx from integrations.
**Watch for:** Other external HTTP requests in the system.
