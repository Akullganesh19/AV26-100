## 2025-02-18 — Request Coalescing

**Gap found:** Naive HTTP client (`frontend/src/api/client.ts`) without any request deduplication/coalescing. Multiple components fetching the same endpoint simultaneously would trigger identical network requests.
**Why it existed:** Default Axios setup doesn't include coalescing. It's often overlooked until network tab shows duplicate requests.
**Built:** Invisible request coalescing layer directly on the `apiClient.get` method. It intercepts `GET` requests, checks an `inFlightRequests` Map using a safely serialized URI (via `apiClient.getUri()`) as the cache key. If a request is pending, it returns the existing Promise instead of making a new one. It automatically cleans up the Map when the Promise settles (via `.finally()`).
**Hot path affected:** Any data-fetching flow where multiple components or hooks fetch the same resource (e.g., reference data, profile info, configuration, dashboards).
**Measurable improvement:** Reduction in redundant network requests. Visible in network tab or backend access logs. Added `console.debug` to log coalesced requests.
**Next opportunity:** Stale-while-revalidate caching or background refresh of frequently-read data.
