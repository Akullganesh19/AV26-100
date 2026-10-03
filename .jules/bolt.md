## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2023-10-04 - Combine Independent Scalar Aggregations
**Learning:** Executing multiple independent scalar aggregations (e.g., `count` and `sum`) on the same SQLAlchemy model as separate queries causes unnecessary database roundtrips.
**Action:** Combine multiple scalar aggregations on the same table into a single `select(func.count(...), func.sum(...))` query to reduce roundtrips and improve performance.
