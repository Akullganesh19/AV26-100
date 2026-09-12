## 2024-06-12 — Unprotected External Integrations and Silent Auth Failures
**Failure point found:** External API calls in `IntegrationService` lacked retry/circuit breaker mechanisms, and JWT cache checks could swallow `HTTPException` inside a blanket `except Exception:` block in `deps.py`.
**Why it existed:** Assumed happy path for 3rd party services and redis cache; quick fail-open attempt swallowed too much.
**Recovery built:** Added `with_retry` and `CircuitBreaker` to `app/core/resilience.py`. Applied them to Algolia, Cloudinary, and SendGrid API calls. Explicitly caught and re-raised `HTTPException` in the redis auth block before falling back.
**Blast radius before:** 3rd party downtime caused unhandled application 500s. Revoked tokens were still allowed if a broader cache error occurred but the initial cache hit threw `HTTPException`.
**Watch for:** Other `except Exception:` blocks swallowing critical HTTP errors.
