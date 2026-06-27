## 2024-05-18 — Request Coalescing
**Gap found:** Multiple React components fetching the same API endpoint simultaneously (e.g. context, profile) caused redundant network requests.
**Why it existed:** The frontend used independent `@tanstack/react-query` or `useEffect` calls relying on standard `axios.get` without a unified deduplication layer at the network level.
**Built:** Intercepted `apiClient.get` to track in-flight requests using a Map based on the URL and sorted query parameters. If a request is already in flight, subsequent identical requests return the same Promise, with response data cloned to prevent shared state mutation.
**Hot path affected:** Every single API GET request across the entire application, particularly noticeable on complex dashboard views.
**Measurable improvement:** Reduces duplicate network payload, lowers latency by skipping redundant round trips, and decreases database load on the backend.
**Next opportunity:** Investigate stale-while-revalidate caching and intelligent background prefetching for predictive UI interactions.
