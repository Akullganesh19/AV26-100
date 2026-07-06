## 2025-01-01 — External Integration Resilience

**Failure point found:** All external integrations (`sync_district_to_algolia`, `send_health_alert_email`, `upload_report_to_cloudinary`, `notify_activity_feed` in `backend/app/api/integrations.py` and `send_alert_notification` in `backend/app/tasks/alerts.py`) lacked fault tolerance. They would crash or propagate exceptions unconditionally upon temporary API outages or network disruptions.

**Why it existed:** The code prioritized happy path delivery for demonstration, missing enterprise-grade wrappers for external calls.

**Recovery built:**
1. Created `backend/app/core/resilience.py` introducing robust `@with_retry` (exponential backoff) and `@with_circuit_breaker` decorators.
2. Composed them on all high-risk, out-of-process API calls, placing the circuit breaker as the outer wrapper and retry logic inside. This ensures transient spikes are retried, but sustained outages trip the breaker, protecting internal application health and minimizing wait times when the external dependency is truly down.

**Blast radius before:** Any temporary SendGrid/Algolia/Cloudinary downtime would bubble up exceptions, potentially blocking report creation, user sync, or silently dropping critical clinical cluster alerts.

**Watch for:** Ensure we do not apply naive retries to non-idempotent endpoints without a dedup/idempotency-key mechanism.
