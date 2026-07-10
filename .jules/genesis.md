## 2025-02-23 — Auto-Retry and DLQ for Alert Dispatch
**Failure point found:** The `send_alert_notification` background task (in `backend/app/tasks/alerts.py`) lacked retry logic and a fallback mechanism. Transient third-party API failures (e.g., SendGrid/Twilio network issues) would cause critical alerts to fail silently and drop forever.
**Why it existed:** The original implementation only had a single `try-except` block logging errors and returning a "failed" status without any resilliency baked in.
**Recovery built:** Added an Auto-Retry mechanism with Exponential Backoff (up to 3 attempts). If retries are exhausted, the system falls back by pushing the failed alert payload into a Redis `dead-letter` queue (DLQ) monitored by the existing `monitor_dlq_depth` celery beat task.
**Blast radius before:** Any transient API glitch would result in permanent failure of dispatching outbreak alerts to health officials, risking mission-critical information loss.
**Watch for:** Other integrations, such as `sync_district_to_algolia` or `upload_report_to_cloudinary` in `backend/app/api/integrations.py`, may also lack retries or circuit breakers for transient failures.
