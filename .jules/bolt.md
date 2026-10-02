## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-10-02 - Combine Multiple Scalar Aggregations
**Learning:** Multiple separate database calls for scalar aggregations (like count and sum) on the same table can introduce unnecessary network latency.
**Action:** Combine them into a single `select(func.count(model.id), func.sum(model.val))` query to optimize query time.
