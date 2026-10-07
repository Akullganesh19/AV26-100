## 2026-10-07 — HTTP GET Request Coalescing
**Gap found:** The frontend Axios client naively fired an independent network request for every `apiClient.get` call, even if identical requests were already in flight.
**Why it existed:** The default Axios behavior lacks built-in request deduplication, leaving it up to individual components or React Query to manage state. In areas without React Query, concurrent component renders could trigger redundant network hits.
**Built:** An invisible request coalescing wrapper around `apiClient.get`. It maintains a Map of in-flight promises keyed by URL and params. If a duplicate request is initiated while the original is pending, it simply returns the existing promise.
**Hot path affected:** Any dashboard or view where multiple child components independently request the same reference data or configuration simultaneously on mount.
**Measurable improvement:** Reduces the number of duplicate outgoing HTTP requests. Measurable via network tab or the added `console.debug('[Phantom] Coalescing duplicate request...')` instrumentation.
**Next opportunity:** Implement a stale-while-revalidate caching mechanism for rarely changing data.
