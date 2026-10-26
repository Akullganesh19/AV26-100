## 2023-10-27 — Request Coalescing
**Gap found:** Identical GET requests made simultaneously resulted in multiple network calls.
**Why it existed:** Naive usage of axios without deduplication or caching for in-flight requests.
**Built:** Request coalescing intercepting apiClient.get to return existing promises for identical requests.
**Hot path affected:** Any component making GET requests simultaneously, such as dashboard widgets or data tables loaded together.
**Measurable improvement:** Reduced duplicate network requests for the same endpoints. Logged via console.debug('🌀 Phantom coalesced request:', key);
**Next opportunity:** Stale-while-revalidate caching for rarely changed config data.
