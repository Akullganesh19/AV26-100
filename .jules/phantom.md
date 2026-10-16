## 2024-05-18 — Request Coalescing
**Gap found:** The frontend API client naively executed independent `GET` requests for the same endpoints concurrently without deduplication.
**Why it existed:** Standard Axios configuration lacks built-in request coalescing for identical in-flight requests.
**Built:** Invisible request coalescing layer wrapping `apiClient.get` that shares the Promise of identical in-flight requests.
**Hot path affected:** Any concurrent data fetching across isolated React components (e.g., identical reference data or user profile requests during page load).
**Measurable improvement:** Reduces duplicate network round-trips; measurable via `console.debug('[Phantom] Coalescing request...')` statements and network tab inspection.
**Next opportunity:** Intelligent background prefetching based on user hover intentions.
