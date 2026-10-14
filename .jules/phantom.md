## 2024-05-24 — Request Coalescing
**Gap found:** Multiple components could trigger simultaneous identical GET requests, wasting network and backend resources.
**Why it existed:** Basic Axios setup without request deduplication.
**Built:** Request coalescing proxy on the Axios GET method that tracks in-flight requests and returns the same Promise to all callers.
**Hot path affected:** Page loads where multiple components fetch the same reference data or metrics.
**Measurable improvement:** Reduced duplicate network requests and lower latency for redundant calls, verifiable via `console.debug` output and network tab.
**Next opportunity:** Stale-while-revalidate client cache.
