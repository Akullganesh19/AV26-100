## 2024-05-24 — External API Call Auto-Retry Added
**Failure point found:** weather_client.get_daily_weather lacked transient error handling in IngestionService.
**Why it existed:** Assumed high reliability of weather data provider without accounting for brief networking blips.
**Recovery built:** Wrapped in with_retry using 3-attempt exponential backoff mechanism.
**Blast radius before:** 100% of pipeline runs would fail entirely if a single district fetching failed during bulk iteration.
**Watch for:** Similar fragility elsewhere in mock API sync logic or integration services without robust retries.
