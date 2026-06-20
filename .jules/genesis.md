## 2024-06-20 — External API calls failing silently or blocking
**Failure point found:** External I/O calls to Algolia, SendGrid, Cloudinary without retry/circuit breakers, missing failure closure for Token Revocation check, and missing retry for database updates in Weather Ingestion.
**Why it existed:** The backend services favored simple happy paths over network resilience logic.
**Recovery built:** Implemented `@with_retry` and `@with_circuit_breaker` across external integrations, enforced closed-fail on `get_current_user` Redis token check, and added transient fail protection to data ingestion loops.
**Blast radius before:** Downstream API failures (Algolia, SendGrid) caused blocking bottlenecks, token check could fail open allowing revoked JWT access, and weather syncs would fully abort on transient db or api timeouts.
**Watch for:** Other integrations directly hitting db APIs without transactional retry bounds or missing token checking blocks elsewhere.
