## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-16 - Combine Independent Scalar Aggregations
**Learning:** Executing multiple independent scalar aggregations (like `count` and `sum`) as separate database queries introduces unnecessary N+1 roundtrip latency.
**Action:** Always combine independent scalar aggregations on the same table into a single `select(func.count(...), func.sum(...))` query to fetch all required statistics in one database roundtrip.
