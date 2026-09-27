## 2026-09-27 — Request Coalescing
**Gap found:** Identical GET requests were being made simultaneously by multiple components (e.g., StrategicMap and Dashboard fetching districts).
**Why it existed:** The app relied purely on React Query's default behavior, but without proper query key alignment or before React Query's cache could populate, multiple components mounting simultaneously bypassed the cache and hit the network independently.
**Built:** A request coalescing interceptor on the global `apiClient`. It maintains a Map of in-flight `GET` requests and returns the same Promise for identical simultaneous requests.
**Hot path affected:** Initial page load and dashboard rendering where multiple widgets fetch the same reference data.
**Measurable improvement:** Reduces redundant network requests on initial render, saving bandwidth and backend processing.
**Next opportunity:** Intelligent prefetch based on navigation patterns or WebSocket integration for live data updates.
