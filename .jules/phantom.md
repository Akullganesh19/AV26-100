## 2024-10-16 — Request Coalescing
**Gap found:** Axios client fired multiple identical GET requests concurrently without deduplication.
**Why it existed:** Default Axios setup doesn't track or coalesce in-flight requests for the same URL/params.
**Built:** Wrapped `apiClient.get` to track and return existing in-flight Promises based on URI and params.
**Hot path affected:** Any component rendering concurrently that fetches the same data.
**Measurable improvement:** Prevents duplicate network round-trips for concurrent identical requests; logged via `console.debug`.
**Next opportunity:** Edge cache headers for static or rarely changed reference data.
