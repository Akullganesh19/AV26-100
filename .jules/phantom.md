## 2024-10-23 — Request Coalescing
**Gap found:** Identical concurrent GET requests to the same API endpoints were not deduplicated.
**Why it existed:** Standard Axios behavior and uncoordinated component mounting caused duplicate requests.
**Built:** Overrode `apiClient.get` to store and share in-flight promises based on URI cache keys.
**Hot path affected:** Initial page loads and uncoordinated data-fetching components across the app.
**Measurable improvement:** Reduces duplicate network round trips, measurable via `console.debug` when requests are coalesced.
**Next opportunity:** Edge cache headers or background refresh for reference data.
