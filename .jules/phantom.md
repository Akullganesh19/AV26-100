## 2024-05-24 — Request Coalescing

**Gap found:** The frontend made multiple, identical HTTP GET requests when several components simultaneously requested the same data (e.g., `/auth/me` on initial load).
**Why it existed:** The `axios` client instance did not have any deduplication or caching logic in place. Each `apiClient.get` invocation spawned a separate network request.
**Built:** An in-memory cache `Map` (Request Coalescing) was implemented by wrapping the `apiClient.get` method. It deterministically hashes the request `url` and `params`. Identical requests wait on a single shared Promise.
**Hot path affected:** Every single concurrent GET request across the entire application, especially during concurrent React component mounts.
**Measurable improvement:** Reduces the number of duplicate network requests to exactly 1 per identical call signature. This directly reduces frontend latency and backend load.
**Next opportunity:** We could introduce stale-while-revalidate semantic caching or ETag/Cache-Control header checks for static asset delivery.
