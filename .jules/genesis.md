## 2024-10-11 — [Title Placeholder]
**Failure point found:**
**Why it existed:**
**Recovery built:**
**Blast radius before:**
**Watch for:**

## 2024-10-11 — [Third-Party API Outage Recovery]
**Failure point found:** External weather API call (`weather_client.get_daily_weather`) inside `run_weather_ingestion` in `backend/app/services/ingestion_service.py` is made via `httpx` and fails entirely if the API returns 500, hangs, or experiences rate limits.
**Why it existed:** The `run_weather_ingestion` background task runs sequentially and assumes `weather_client.get_daily_weather` will always succeed.
**Recovery built:** Will implement an exponential backoff auto-retry for `httpx` HTTP requests in `WeatherClient`.
**Blast radius before:** If the OpenMeteo API hangs or returns intermittent errors, weather data for all following districts wouldn't be fetched and the ingestion pipeline would crash and mark the pipeline run as "failed".
**Watch for:** Other integrations in `IntegrationService` like Algolia and Sendgrid using external API clients might need similar backoff strategies.
