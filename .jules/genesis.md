## 2024-11-20 — External Call Fragility
**Failure point found:** External API calls (weather, Algolia, SendGrid, Cloudinary) were lacking retry logic and were not resilient to transient failures.
**Why it existed:** Assumed external APIs would always be responsive and successful on the first try.
**Recovery built:** Created `with_retry` function with exponential backoff and wrapped external calls.
**Blast radius before:** Silent failure in the pipeline or loss of user notification in case of temporary network glitches or third-party outages.
**Watch for:** Other integrations or synchronous DB operations that could block or fail intermittently.
