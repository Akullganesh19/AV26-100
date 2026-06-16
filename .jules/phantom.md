## 2024-06-15 — API Client Enhancements

**Gap found:** The application currently makes API calls using `axios` directly in several components, bypassing the configured `apiClient`. This means no centralized request management. More critically, there is no request coalescing or caching for `GET` requests, leading to potential duplicate network calls when multiple components mount and request the same or similar data simultaneously, and no cache to prevent hitting the network on subsequent rapid requests.
**Why it existed:** Historical rapid development; components were built in isolation and imported `axios` directly instead of using the shared `apiClient` that was likely created later.
**Built:** An intelligent caching and request coalescing layer in `apiClient`. It intercepts `GET` requests, coalesces simultaneous identical requests into a single network promise, and caches the result with a TTL (Time-To-Live). We also updated all components to use this optimized `apiClient` instead of raw `axios`.
**Hot path affected:** Every data-fetching operation in the application, including Dashboard stats, Strategic Map overlays, Tactical Alerts, and Diagnostics Center.
**Measurable improvement:** Reduced duplicate network requests to exactly 1 per unique endpoint+params combination during the TTL window. Reduced latency for subsequent identical data fetching to ~0ms.
**Next opportunity:** Background sync for non-critical writes (e.g., acknowledged alerts) and optimistic UI updates to make actions feel instantaneous.
