## 2024-05-24 — Request Coalescing (Deduplication)
**Gap found:** Multiple React components (like charts, maps, and stats) making identical API calls (e.g., to `/districts` or `/districts/stats`) simultaneously on page load without any request deduplication.
**Why it existed:** The frontend used a basic Axios instance relying purely on React Query's default behavior, which may still result in race conditions or duplicate network flights during initial mount if components mount at exactly the same time before the cache is populated.
**Built:** Wrapped `apiClient.get` with an in-flight request Map. Identical GET requests (matching URL and serialized params) made concurrently now share the same underlying Promise.
**Hot path affected:** Initial dashboard and map loads where multiple widgets request the same baseline data.
**Measurable improvement:** Reduces redundant network requests on heavy dashboard renders.
**Next opportunity:** Implement stale-while-revalidate caching with TTL for reference data.
