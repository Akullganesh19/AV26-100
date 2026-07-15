## 2026-07-15 — Request Coalescing

**Gap found:** The frontend `apiClient` in `frontend/src/api/client.ts` lacked request coalescing, meaning multiple React components requesting the same API endpoint simultaneously (e.g., during page load) would fire duplicate, redundant network requests.
**Why it existed:** The `axios` instance was a simple wrapper that added authentication headers and handled 401s, but did not track in-flight requests to deduplicate them.
**Built:** Added a request coalescing map (`inFlight`) and monkey-patched `apiClient.get` to intercept outgoing GET requests. If an identical request (matching URL and query params) is already in-flight, it returns the existing Promise instead of firing a new network request.
**Hot path affected:** All data fetching across the frontend app that utilizes `apiClient.get`, especially on heavy pages with multiple components depending on the same initial data.
**Measurable improvement:** Significantly reduces identical concurrent API requests on initial page loads and component mounts, reducing network latency and backend load.
**Next opportunity:** Investigate frontend stale-while-revalidate caching and background pre-fetching for even faster perceived load times.
