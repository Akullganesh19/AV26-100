## 2026-09-09 — Request Coalescing

**Gap found:** Multiple components on dashboards (like maps, alerts, stats) fetch the exact same data endpoints simultaneously, causing duplicate network requests and unneeded backend load.
**Why it existed:** Standard React components and API clients naively execute requests when mounted without coordinating flight status.
**Built:** Request coalescing in `apiClient.ts` that deduplicates identical in-flight GET requests, returning the same Promise to all callers.
**Hot path affected:** Initial dashboard load and page navigations, where multiple widgets fetch shared reference data (districts, active scenarios, alerts).
**Measurable improvement:** Reduces duplicate API requests during component mounting storms, lowering network bandwidth and backend database contention.
**Next opportunity:** Stale-while-revalidate caching for rarely changing district data.
