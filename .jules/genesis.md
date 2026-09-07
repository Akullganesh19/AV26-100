## 2024-05-18 — Added Auto-Retry with Exponential Backoff
**Failure point found:** External HTTP requests and IO operations (SendGrid, Algolia, Cloudinary, WeatherAPI) lacked retry logic and failed silently on transient errors.
**Why it existed:** Assumed third-party dependencies are highly available and ignored network volatility.
**Recovery built:** Created `with_retry` mechanism providing automatic retries with exponential backoff for third party IO integrations.
**Blast radius before:** Any transient API failure would cause full task aborts resulting in lost health alerts, missing ingestion data, and missing dashboard data.
**Watch for:** Other integrations, database calls, or external tasks that still assume perfect network reliability.
