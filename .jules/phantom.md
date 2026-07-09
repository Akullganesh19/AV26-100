## 2026-07-09 — Request Coalescing in apiClient
**Gap found:** The frontend `apiClient` (axios) naively executed every `GET` request without deduplication, causing components mounting concurrently to trigger identical network requests multiple times.
**Why it existed:** Standard axios behavior out-of-the-box doesn't coalesce requests.
**Built:** Request coalescing in `frontend/src/api/client.ts` via an overridden `apiClient.request` method that caches Promises in an `inFlight` Map keyed by method, url, and params.
**Hot path affected:** Any dashboard or page where multiple child components fetch the same reference data (e.g., config, alerts, common resources) simultaneously.
**Measurable improvement:** Reduces duplicate network requests. Reduces backend load and latency by returning the same shared Promise to all concurrent callers for identical endpoints.
**Next opportunity:** Implement a stale-while-revalidate caching layer for frequently accessed but rarely changed data.
