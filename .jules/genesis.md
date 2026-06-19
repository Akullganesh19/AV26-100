## 2026-06-19 — Unprotected External Dependency Failures

**Failure point found:** External integrations (SendGrid, Algolia, Cloudinary) in `backend/app/api/integrations.py` and alert notification dispatch in `backend/app/tasks/alerts.py` were entirely unprotected. `cloudinary.uploader.upload` was also a blocking synchronous call in an async function.
**Why it existed:** Assumed happy-path reliability of external third-party services.
**Recovery built:**
1. Centralized resilience patterns in `backend/app/core/resilience.py` with `@with_retry`, `@with_circuit_breaker`, and `@with_dead_letter_queue` decorators.
2. Applied `@with_retry` and `@with_circuit_breaker` to the `sync_district_to_algolia`, `send_health_alert_email`, and `upload_report_to_cloudinary` methods in `backend/app/api/integrations.py`.
3. Added `@with_retry` and `@with_dead_letter_queue` to `send_alert_notification` in `backend/app/tasks/alerts.py` to catch dispatch failures.
4. Wrapped the synchronous blocking `cloudinary.uploader.upload` call with `asyncio.to_thread` to prevent event loop blocking.
**Blast radius before:** Any network hiccup, API throttling, or temporary third-party outage would result in unhandled exceptions, potentially taking down parts of the application or failing to send critical health alerts entirely.
**Watch for:** Other third-party integrations (e.g. `notify_activity_feed` via StreamChat if implemented) or database transactions lacking similar protections, and synchronous blocking code hiding inside async functions.
