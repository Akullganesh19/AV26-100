## 2024-05-15 — Weather Ingestion API Protection
**Failure point found:** Weather data ingestion pipeline in `IngestionService.run_weather_ingestion` was missing retry logic when calling the external `weather_client.get_daily_weather` API.
**Why it existed:** The ingestion script was designed assuming a happy path where the external weather API is always available and network requests never fail transiently.
**Recovery built:** Added exponential backoff retry mechanism (using `with_retry`) to `weather_client.get_daily_weather`.
**Blast radius before:** If the third-party weather API failed transiently (e.g. rate limits, brief network hiccups), the entire pipeline run would abort and no subsequent districts would get their data updated, leading to stale environmental features for predictions.
**Watch for:** Other external API calls in background jobs or third-party integrations (e.g., SendGrid, Algolia) that lack retry policies.
