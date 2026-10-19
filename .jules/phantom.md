## 2023-10-24 — Request Coalescing Added
**Gap found:** No request coalescing for identical API calls, causing redundant network requests when multiple components fetched the same endpoint simultaneously.
**Why it existed:** The app relied on raw Axios instance methods which do not naturally deduplicate concurrent identical GET requests.
**Built:** Intercepted `apiClient.get` to cache the Promise of in-flight requests, returning the shared Promise to all callers requesting the same URI.
**Hot path affected:** Any dashboard or page where multiple child components fetch reference data, config, or shared resources on mount.
**Measurable improvement:** Reduces redundant network requests to 1. Measurable by counting `[Phantom] Coalescing request: ...` debug logs in the browser console.
**Next opportunity:** Edge caching for static reference data.
