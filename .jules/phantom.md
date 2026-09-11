## 2024-05-18 — Request Coalescing

**Gap found:** The frontend app naively fires off duplicate API requests if multiple components query the same endpoint simultaneously.
**Why it existed:** Native Axios behavior paired with decoupled UI components causing duplicate network calls.
**Built:** Request coalescing wrapper around `apiClient.get` that intercepts duplicate in-flight requests and returns the same Promise.
**Hot path affected:** Any simultaneous identical GET request across the app (like refetching dashboards or simultaneous component mount fetches).
**Measurable improvement:** Prevents duplicate network round-trips for the same exact data during the same render tick/in-flight window, reducing latency and server load.
**Next opportunity:** Investigate API response stale-while-revalidate caching layer for reference data.
