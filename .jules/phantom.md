## 2024-05-18 — Request Coalescing
**Gap found:** Naive GET requests in `frontend/src/api/client.ts` caused multiple components fetching the same endpoint concurrently to trigger redundant network requests.
**Why it existed:** It was a simple Axios configuration without any stateful caching or deduplication mechanism across the app.
**Built:** Request coalescing for `apiClient.get` using a Map to track in-flight requests and return a shared promise for identical concurrent queries.
**Hot path affected:** Any dashboard or data-heavy view where multiple UI components request the same data simultaneously.
**Measurable improvement:** Reduced redundant network traffic by returning the same promise for duplicate in-flight GET requests.
**Next opportunity:** Implement stale-while-revalidate caching to further improve perceived performance on frequently visited data.
