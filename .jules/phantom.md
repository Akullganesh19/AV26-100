## 2025-03-02 — Request Coalescing

**Gap found:** 10 components each fetched the same endpoint independently because naive `axios` was being directly used across the app, avoiding any centralized API client logic.
**Why it existed:** As the app scaled and dashboards/maps grew, multiple components were built independently requesting data on mount without centralized query caching or request deduplication.
**Built:** An intelligent request coalescing layer in `apiClient`. It intercepts simultaneous `GET` requests for the same URL and parameters, returning the same Promise to all callers instead of firing redundant network calls.
**Hot path affected:** Dashboard, Maps, and Simulation Labs fetching heavy datasets (like `district` geometries or metrics) on page load.
**Measurable improvement:** Multiple identical simultaneous GET requests are collapsed into a single HTTP request, saving bandwidth and reducing backend load significantly.
**Next opportunity:** Stale-while-revalidate caching pattern for reference datasets.
