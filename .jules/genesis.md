## 2026-06-29 — Redis-Backed Circuit Breaker & Retry
**Failure point found:** External integrations (Algolia, SendGrid, Cloudinary) failed silently or had no retry/circuit breaker mechanisms, risking cascading failures or infinite hangs if APIs were down.
**Why it existed:** Initial MVP speed; no defensive coding applied to third-party endpoints yet.
**Recovery built:** Created `with_circuit_breaker` and `with_retry` decorators in `app/core/resilience.py` backed by Redis for distributed state, protecting `IntegrationService` operations. It also fails gracefully (OPEN to CLOSED) if Redis goes down, to avoid taking down the whole app when infrastructure fails.
**Blast radius before:** Complete app halt or unhandled exceptions on any external network flap.
**Watch for:** Other direct DB or API calls that don't pass through this resilience layer.
