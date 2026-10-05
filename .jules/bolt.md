## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-16 - Combining Multiple Independent Scalar Aggregations
**Learning:** Making separate sequential asynchronous database queries for multiple scalar aggregations (like count and sum) on the same SQLAlchemy model results in unnecessary database roundtrips and N+1 patterns, reducing route performance.
**Action:** Combine multiple independent scalar aggregations into a single `select(func.count(...), func.sum(...))` query to execute them simultaneously in one roundtrip.
