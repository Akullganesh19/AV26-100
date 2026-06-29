## 2024-06-29 — Request Coalescing
**Gap found:** The frontend API client naively executed every `apiClient.get` request independently, even if identical requests (same URL and params) were triggered concurrently by different components mounting at the same time.
**Why it existed:** The default Axios setup does not perform deduplication natively. Each React component requesting data acts in isolation.
**Built:** Intercepted `apiClient.get` to track in-flight GET requests in a Map using a deterministic cache key. Concurrent requests to the same URL with the same sorted parameters now await and share a single underlying Promise, deep-cloning the final data to prevent reference leakage across components.
**Hot path affected:** Any dashboard or page where multiple sub-components (e.g., charts, cards) fetch the same reference or aggregation data on load.
**Measurable improvement:** Reduces redundant network requests on load. Can be measured by inspecting network dev tools on heavy pages—duplicate identical concurrent `GET` requests will be completely eliminated.
**Next opportunity:** Background Sync / Offline Mutation Queue for critical writes.
