## 2024-05-24 — Unprotected API Calls & No Fallbacks

**Failure point found:**
- External integration calls in `backend/app/api/integrations.py` (`sync_district_to_algolia`, `send_health_alert_email`, `upload_report_to_cloudinary`) lack retry logic for transient network or API failures.
- `weather_client` is imported in `backend/app/services/ingestion_service.py` but is missing from `backend/app/api/integrations.py` entirely! This is a hard crash waiting to happen (and actually already happening as `ModuleNotFoundError` is inevitable).
- Background alert dispatches in `backend/app/tasks/alerts.py` (`send_alert_notification`) simulate a third-party call but only try once and return `"status": "failed"` without queuing for retry.

**Why it existed:** MVP rushed development; assumed external APIs are 100% available and forgot to implement the `WeatherClient`.

**Recovery built:**
- Implemented `with_retry_async` decorator pattern for asynchronous operations with exponential backoff (up to 3 retries).
- Applied retry logic to Algolia sync, SendGrid emails, and Cloudinary uploads.
- Built a mock `WeatherClient` in integrations to prevent the ingestion pipeline from crashing on `ModuleNotFoundError`.
- Wrapped alert dispatches in the retry loop.

**Blast radius before:** Silent failure of notifications, lost reports, failed search index syncs, and outright crash on ingestion service.
**Watch for:** Other mocked third-party integrations or missing clients.
