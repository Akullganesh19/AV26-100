## 2024-05-24 — Add Automatic Retries for Third-Party Integrations
**Failure point found:** External integrations (SendGrid, Algolia, Cloudinary) in `backend/app/api/integrations.py` had no retry mechanisms on failure.
**Why it existed:** Assumed APIs were 100% reliable.
**Recovery built:** Built `with_retry` decorator for automatic retries with exponential backoff.
**Blast radius before:** Transient API errors caused silent failures in crucial logic (like health alerts).
**Watch for:** Other integrations lacking retry mechanisms (e.g. webhook receivers).
