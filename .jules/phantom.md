## 2024-10-27 — Request Coalescing
**Gap found:** The API client lacked request deduplication, allowing identical simultaneous requests for the same resource.
**Why it existed:** The naive axios client implementation didn't have any in-flight request tracking.
**Built:** Added an interceptor-like wrapper over `apiClient.get` to store in-flight promises in a Map and return the shared promise for identical concurrent requests, utilizing `apiClient.getUri` for exact cache key generation.
**Hot path affected:** All data fetching routes via GET requests across components, especially heavily used during React rendering and dashboard loading.
**Measurable improvement:** Reduces the number of duplicate network requests during concurrent component renders, directly observable via Network tab and the added `console.debug` logs.
**Next opportunity:** Implement a stale-while-revalidate caching layer for infrequently updated data.
