## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2024-10-04 - Optimize Multiple Scalar Aggregations on the Same Table
**Learning:** Executing multiple independent scalar aggregations (like count and sum) on the same table via separate `db.execute` calls is an N+1 pattern that incurs unnecessary database roundtrips.
**Action:** Combine multiple scalar aggregations into a single `select(func.count(...), func.sum(...))` query to execute them in one roundtrip for improved performance.
