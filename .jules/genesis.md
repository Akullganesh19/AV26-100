## 2024-05-18 — Healing Network I/O

**Failure point found:** All third-party integrations (Algolia, Sendgrid, Cloudinary, etc) lacked retry mechanisms. The asynchronous task for sending alerts (`send_alert_notification`) and methods within `IntegrationService` would silently drop critical messages on transient network errors.
**Why it existed:** Assumed happy-path network operations during initial implementation.
**Recovery built:** Created an exponential backoff retry mechanism (`app.core.healing.with_retry`) and decorated all external asynchronous operations in `app.api.integrations` and `app.tasks.alerts`.
**Blast radius before:** Silent failure in the event of any momentary network partition or API rate limit. Important health alerts and data sync operations would drop.
**Watch for:** Other integrations directly invoking HTTP clients without wrapping them in the retry logic.
