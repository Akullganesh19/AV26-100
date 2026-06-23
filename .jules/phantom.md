## 2026-06-23 — Request Coalescing
**Gap found:** The frontend HTTP client (`apiClient.ts` using Axios) did not deduplicate concurrent identical GET requests. If multiple components requested the same resource simultaneously on render, multiple identical network requests would be fired.
**Why it existed:** Naive usage of `axios.create()` without custom interceptors or promise caching for concurrent requests.
**Built:** An invisible infrastructure layer directly into `apiClient.get` that maintains a `Map` of in-flight requests keyed by URL and query parameters. Concurrent requests for the same resource now return the same pending Promise, coalescing N network requests into 1.
**Hot path affected:** Any page load where multiple components query the same data (e.g. user profile, config, reference data) or when React's strict mode double-renders components.
**Measurable improvement:** Reduces the number of network requests on complex page loads, dropping latency and preventing server thundering herds from a single client.
**Next opportunity:** Edge caching headers or intelligent pre-fetching for predicted navigation paths.
