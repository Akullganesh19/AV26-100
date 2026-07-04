## 2026-07-04 — Request Coalescing Middleware
**Gap found:** The frontend `apiClient` used basic Axios without any deduplication. Multiple React components requesting the same identical resource (like current user profile or district status) during a render cycle would spawn multiple identical HTTP GET requests.
**Why it existed:** The default Axios configuration does not inherently support request coalescing, and component architectures often lead to isolated data fetching rather than centralized state management.
**Built:** A lightweight request coalescing middleware on `apiClient.get`. It generates a deterministic cache key using the URL and sorted query parameters, and maps it to the in-flight Promise. Subsequent identical requests return the existing Promise rather than initiating a new network call.
**Hot path affected:** Any concurrent frontend rendering that relies on shared resources (e.g., loading dashboards, maps, and profile widgets simultaneously).
**Measurable improvement:** Reduces redundant concurrent network GET requests to 1, lowering both client-side latency and backend load spikes.
**Next opportunity:** Investigate Edge Cache Headers (Cache-Control and ETags) for static or slowly changing reference data, and implement stale-while-revalidate patterns for the frontend data stores.
