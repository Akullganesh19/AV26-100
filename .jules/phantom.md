## 2025-07-06 — Request Coalescing and Application Caching Layer

**Gap found:** Heavy, redundant inferences and analytical queries were triggered by identical frontend page loads/rerenders. The `PredictionService.predict_batch` and DB aggregate queries (`get_district_stats`) ran independently on every request, wasting DB connections, model execution time, and Redis capacity.

**Why it existed:** The backend assumed each endpoint request genuinely represented unique, time-sensitive work. The frontend naive Axios usage triggered independent GET requests across separate UI components during a single page render (e.g., config, alerts, stats) instead of reusing pending network calls.

**Built:**
1. **Request Coalescing:** Frontend `apiClient.get` now intercepts duplicate in-flight identical network calls, returning a single shared Promise.
2. **Infrastructure Caching:** Added a transparent `redis` caching tier with an intelligent TTL mechanism. `list_districts` and `get_district_detail` (which rely heavily on predictions that roll over daily) cache for 1 hour. Dashboard metrics (`get_district_stats`) cache for 1 minute.
3. **Async Backgrounding:** Introduced `fire_and_forget` in backend to serialize and save to Redis off the hot path, preventing latency spikes while ensuring strong execution referencing.

**Hot path affected:** Application launch (`list_districts` payload) and the primary Strategic Map / Dashboard initializers.

**Measurable improvement:** Page load API requests reduced due to coalescing; subsequent loads reduced backend P95 latency substantially by omitting sequential model inferences entirely.

**Next opportunity:** Edge-caching immutable analytical reports using CDNs (e.g. S3 CloudFront) directly rather than routing through FastAPI `reports.py`.
