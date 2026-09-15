## 2024-05-24 — External API resilience
**Failure point found:** External API integrations (Algolia, Sendgrid, Cloudinary) lacked retry mechanisms and circuit breakers, causing silent failures or cascading errors during network glitches.
**Why it existed:** Assumed external APIs would always be responsive and successful.
**Recovery built:** Implemented `with_retry` and `CircuitBreaker` utility classes, applying them to Algolia syncing, Sendgrid emailing, and Cloudinary uploads.
**Blast radius before:** Any external API failure could result in lost alerts, failed report uploads, and unsynced districts, impacting end-users without warning.
**Watch for:** Other integrations, such as GetStream, still lack these protections and may be future failure points.
