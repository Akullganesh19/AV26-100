## $(date +%Y-%m-%d) — Request Coalescing Added
**Gap found:** The frontend application makes duplicate concurrent requests for the same endpoints (e.g., dashboard stats, identical queries triggered by re-renders or multiple components loading simultaneously), leading to unnecessary network traffic and backend load.
**Why it existed:** The `apiClient` was instantiated with a basic Axios configuration without interceptors for request deduplication. React components independently fetched data via raw `axios` calls instead of utilizing the centralized client.
**Built:** An invisible request coalescing layer in `frontend/src/api/client.ts`. It overrides the `apiClient.get` method to track in-flight promises. Duplicate concurrent requests for the identical URL and params are merged and return the same Promise. All frontend components were refactored to use this client.
**Hot path affected:** Every standard GET request made through `apiClient` (including data fetching on initial loads for strategic maps, dashboard stats, tactical alerts).
**Measurable improvement:** Reduces the number of outgoing HTTP GET requests when multiple components request the same data simultaneously or under rapid re-renders. Check the Network tab in DevTools; fewer identical API requests should be dispatched simultaneously.
**Next opportunity:** Edge caching for static data like districts list.
