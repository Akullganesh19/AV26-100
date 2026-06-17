## 2024-05-18 — Request Coalescing Added
**Gap found:** The frontend application made multiple identical concurrent requests (e.g. hitting the same simulation or analytics endpoints multiple times at once on render) and bypassed the centralized API client in multiple views by using raw `axios`.
**Why it existed:** The code had grown quickly, with different components fetching identical data simultaneously and importing `axios` directly for convenience.
**Built:** A central request coalescing infrastructure inside `frontend/src/api/client.ts` that intercepts and tracks `GET` requests, ensuring simultaneous duplicate requests return the same `Promise` without hitting the network multiple times. Refactored all raw `axios` usages to use the centralized `apiClient`.
**Hot path affected:** Any dashboard or view rendering multiple components relying on identical API data simultaneously (e.g. Dashboard, StrategicMap).
**Measurable improvement:** Reduction in duplicate network requests during initial page loads or refresh cycles, easily visible in the network tab.
**Next opportunity:** Implement a robust caching layer with stale-while-revalidate for static map/district data to further reduce unnecessary network traffic.
