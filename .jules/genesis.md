## 2023-11-03 — Weather API Ingestion Resiliency
**Failure point found:** `run_weather_ingestion` fails entirely if a single district's `get_daily_weather` API call throws an error.
**Why it existed:** The external API call was made inside a loop without its own `try/catch` and without retry logic, making the entire pipeline run brittle to transient network/API issues.
**Recovery built:** Wrapped `weather_client.get_daily_weather` with exponential backoff (`with_retry`) and added an inner `try/catch` to log the failure and `continue` to the next district without failing the entire run.
**Blast radius before:** 100% data loss for all remaining districts in that day's pipeline run.
**Watch for:** Other background tasks or loops calling external services without inner error boundaries.
