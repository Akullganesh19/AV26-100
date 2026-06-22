## 2025-02-12 — Request Coalescing
**Gap found:** Naive GET requests lacking deduplication on identical concurrent calls
**Why it existed:** Default Axios configuration
**Built:** Request coalescing for identical concurrent GET requests in API client
**Hot path affected:** Frontend data fetching
**Measurable improvement:** Reduces duplicate network calls by returning the same unresolved Promise
**Next opportunity:** Implement cache with stale-while-revalidate for read-heavy operations
