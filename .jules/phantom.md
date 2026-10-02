## 2026-10-02 — Request Coalescing Pipeline
**Gap found:** Multiple components making identical, simultaneous API calls bypassing centralized client configuration.
**Why it existed:** Naive usage of bare axios per component rather than using the centralized apiClient setup.
**Built:** An in-flight request map overlaying the apiClient.get method to coalesce identical, concurrent requests into a single promise.
**Hot path affected:** Initial dashboard load, which triggers multiple dependent or overlapping data fetches.
**Measurable improvement:** Reduces duplicate network round-trips for shared resources by returning the same promise for concurrent requests.
**Next opportunity:** Intelligent client-side caching of infrequently changing reference data with stale-while-revalidate.
