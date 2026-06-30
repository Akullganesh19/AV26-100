## 2026-06-30 — Request Coalescing
**Gap found:** Naive infrastructure existed where multiple identical GET requests could be fired concurrently by different components on page load, leading to redundant network calls and wasted server throughput.
**Why it existed:** Standard Axios behavior does not deduplicate requests. Components fetch data independently upon mounting.
**Built:** Implemented an in-flight request tracker (`Map`) in the global `apiClient.get` interceptor. It generates a deterministic cache key based on the URL and sorted query parameters, returning a shared promise for identical concurrent requests.
**Hot path affected:** Every API GET request across the entire frontend application (especially page loads with multiple widgets requesting the same reference data).
**Measurable improvement:** Reduced redundant identical network calls to exactly 1. Lowered backend load and reduced perceived latency as all subscribers resolve simultaneously.
**Next opportunity:** Implement an intelligent stale-while-revalidate caching layer or background prefetching based on user navigation.
