## 2026-10-01 — Request Coalescing Infrastructure
**Gap found:** Duplicate identical API calls could be fired off before previous ones finish, wasting bandwidth and server resources. Hardcoded `axios` usages bypassed the central API client.
**Why it existed:** Quick iteration led to direct `axios` usage instead of a centralized client; default React Query behavior doesn't deduplicate concurrent initial fetches across unlinked components.
**Built:** Request coalescing wrapper on the central `apiClient.get` method, and refactored all direct `axios` calls to route through this central client.
**Hot path affected:** Every data-fetching GET request on page load and simulation updates.
**Measurable improvement:** Reduced duplicate network requests to 0 for concurrent identical queries.
**Next opportunity:** Edge caching for static reference data.
