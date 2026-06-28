## 2024-06-28 — Resilient Integration Service
**Failure point found:** External integrations (Algolia, SendGrid, Cloudinary) in `backend/app/api/integrations.py` had no retry mechanisms, idempotency guards, or circuit breakers. Transient network failures or third-party API downtime would cause uncaught exceptions and fail user requests.
**Why it existed:** Initial naive implementation without reliability engineering.
**Recovery built:** Implemented `with_retry` and `with_circuit_breaker` decorators in `backend/app/core/resilience.py`. Applied these self-healing wrappers to all integration methods. Added Redis-backed idempotency guards for email alerts to prevent duplicate critical notifications.
**Blast radius before:** Any transient API failure would return 500 errors to users and drop critical operations like sending health alerts or indexing search data.
**Watch for:** Other external HTTP calls (e.g., OpenMeteo) lacking resilience decorators.
