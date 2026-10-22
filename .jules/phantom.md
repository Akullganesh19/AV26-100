## 2024-06-03 — Request Coalescing Layer
**Gap found:** The frontend API client issued independent GET requests without deduplication, causing components mounting simultaneously to redundantly fetch the same endpoints.
**Why it existed:** The native Axios setup processes every request individually by default.
**Built:** An in-flight request coalescing wrapper around `apiClient.get` that multiplexes duplicate concurrent fetches into a single network call.
**Hot path affected:** Any dashboard or data-heavy view where multiple components independently query the same reference data or state on mount.
**Measurable improvement:** Reduces duplicate concurrent network calls. Measurable via Network tab or the newly added `console.debug('[Phantom] Coalesced request:')` instrumentation.
**Next opportunity:** Stale-while-revalidate caching mechanism to serve immediate data while background refreshing.
