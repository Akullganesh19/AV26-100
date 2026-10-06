## 2026-10-06 — Request Coalescing

**Gap found:** The frontend `apiClient` used basic Axios without deduplication, meaning multiple components mounting simultaneously and requesting the same data would fire duplicate API requests.
**Why it existed:** Simple abstraction over Axios; no global request deduplication layer.
**Built:** Invisible request coalescing layer directly on `apiClient.get`. In-flight GET requests are tracked by URL and parameters; identical subsequent requests immediately return the same Promise instead of hitting the network.
**Hot path affected:** Any page where multiple components independently query the same endpoint (e.g., fetching a dashboard configuration or user profile).
**Measurable improvement:** Reduces duplicate network traffic and server load during complex component tree mounts. Measurable via `console.debug("🌀 Phantom: Coalesced duplicate GET request...")` traces.
**Next opportunity:** Stale-while-revalidate caching pattern for frequently accessed but rarely changed data (e.g., config, reference data).
