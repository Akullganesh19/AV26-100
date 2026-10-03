## 2026-10-03 — Request Coalescing
**Gap found:** Identical API calls made multiple times within one page load, specifically naive raw `axios` fetching without caching or deduplication.
**Why it existed:** Quick implementation using raw axios instead of configuring the centralized apiClient with request deduplication logic.
**Built:** Request coalescing for GET requests attached to the centralized `apiClient`. Refactored all raw `axios` usage to leverage `apiClient`.
**Hot path affected:** Components fetching identical reference data (e.g., stats, alerts) at the same time.
**Measurable improvement:** Concurrent identical GET requests are squashed into a single network call.
**Next opportunity:** Implement a robust background syncing mechanism for mutations.
