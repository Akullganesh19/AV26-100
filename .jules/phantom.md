## 2024-05-30 — Request Coalescing Added
**Gap found:** Multiple identical simultaneous GET requests were allowed via the API client.
**Why it existed:** The frontend used a standard Axios instance without request deduplication.
**Built:** A wrapper around `apiClient.get` that tracks in-flight requests using a Map and returns the existing promise for identical concurrent requests.
**Hot path affected:** Any component that triggers data fetching on mount (e.g., dashboards, reference data).
**Measurable improvement:** Reduced redundant network calls; measurable via `[Phantom]` debug logs in the browser console.
**Next opportunity:** Stale-while-revalidate caching layer for reference data.
