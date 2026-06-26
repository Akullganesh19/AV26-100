## 2024-06-27 — Request Coalescing
**Gap found:** Multiple identical concurrent API requests hit the network naively.
**Why it existed:** There was no tracking of in-flight `apiClient.get` requests in the central Axios configuration.
**Built:** A Map that tracks in-flight GET requests, intercepting `apiClient.get` and returning a shared Promise if a request with identical URL and params is already running.
**Hot path affected:** Initial data fetches and concurrent component mounts where multiple UI components request the exact same resource.
**Measurable improvement:** Reduces duplicate network round trips, conserving both client bandwidth and server throughput on concurrent loads.
**Next opportunity:** Implement a true cache layer using `stale-while-revalidate` for configuration and reference data.
