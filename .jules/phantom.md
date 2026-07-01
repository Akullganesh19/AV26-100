## 2024-07-22 — Request Coalescing
**Gap found:** The frontend HTTP client (`apiClient` using Axios) did not deduplicate concurrent identical GET requests, allowing components on the same page load to independently fetch the same endpoint simultaneously.
**Why it existed:** Default Axios behavior naively issues a network request for every `get()` call, and without an intelligent data-fetching library or custom interceptor, no deduplication occurs.
**Built:** An invisible request coalescing layer in `frontend/src/api/client.ts` that intercepts `apiClient.get`. It generates a consistent cache key (URL + sorted query parameters) and returns a shared `Promise` for concurrent identical requests.
**Hot path affected:** Any dashboard or view where multiple components (e.g., map, sidebar, chart) fetch the same aggregate statistics or district data concurrently on mount.
**Measurable improvement:** Reduces redundant network requests for identical data to exactly one per unique set of query parameters while the request is in flight. This minimizes server load and decreases client-side latency.
**Next opportunity:** Implement a stale-while-revalidate caching mechanism or background prefetching for frequently-read data.
