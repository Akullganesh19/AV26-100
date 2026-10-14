## 2023-10-24 — Request Coalescing

**Gap found:** Identical GET API calls made multiple times within one page load, wasting network throughput and causing duplicate work.
**Why it existed:** Native axios usage with no built-in deduplication strategy.
**Built:** Request coalescing for all GET requests on the global `apiClient`. In-flight requests are tracked by URL and parameters; duplicates return the exact same Promise.
**Hot path affected:** Every data-fetching React component using the central `apiClient`.
**Measurable improvement:** Reduced network requests on initial load or frequent polling. Verified via `console.debug` tracking coalesced hits.
**Next opportunity:** Stale-while-revalidate caching pattern for reference data.
