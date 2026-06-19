## 2024-06-19 — Request Coalescing Added
**Gap found:** Identical API calls made multiple times within one page load without request coalescing — 10 components each fetch the same endpoint independently causing redundant load.
**Why it existed:** The default axios instance just made requests naively; React frequently mounts multiple components that might need the exact same stats or map data.
**Built:** Request coalescing in `frontend/src/api/client.ts` to intercept `apiClient.get`. Identical requests in-flight return the exact same Promise, eliminating the thundering herd on page load.
**Hot path affected:** Every single data-fetching query (like districts data on map, dashboard stats, tactile alerts).
**Measurable improvement:** Backend request load is reduced substantially when multiple components request similar data on identical parameters simultaneously, avoiding latency for users.
**Next opportunity:** Implement a Service worker for offline capability and intelligent cache layer with stale-while-revalidate for edge caching.
