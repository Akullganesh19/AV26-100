## 2024-05-23 — Request Coalescing
**Gap found:** Identical GET requests (like concurrent component renders fetching the same user profile or config) hit the server multiple times simultaneously.
**Why it existed:** Naive fetch implementation without deduplication on the client side.
**Built:** Intercepted `apiClient.get` to maintain a Map of in-flight requests. If a request is already flying for a given URL and config, subsequent calls return the same promise.
**Hot path affected:** Any data fetching happening concurrently on page load or navigation.
**Measurable improvement:** Reduced duplicate network requests and database queries on the backend by coalescing them at the source.
**Next opportunity:** Implement stale-while-revalidate caching.
