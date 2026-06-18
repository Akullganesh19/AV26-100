## 2026-06-18 — Request Coalescing
**Gap found:** Multiple components on the same page were sending duplicate concurrent API requests for the same exact data, lacking connection coalescing. Many components bypassed the centralized `apiClient` completely.
**Why it existed:** Components were naively written to fetch data independently using direct `axios` imports, without utilizing global state or a shared request cache.
**Built:** Request coalescing middleware on `apiClient.get`. It intercepts identical inflight requests (matching URL and query params), caches the initial promise, and returns the same promise to subsequent callers.
**Hot path affected:** Initial dashboard rendering and rapid navigation across all primary views.
**Measurable improvement:** Prevents thundering herd of identical backend requests on complex pages, significantly reducing server load and saving client network resources.
**Next opportunity:** Implement a Stale-While-Revalidate caching layer on top of coalescing to enable instant rendering of reference data and configuration schemas.
