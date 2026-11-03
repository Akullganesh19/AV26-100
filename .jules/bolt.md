## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-15 - Batched Scalar Aggregate Queries
**Learning:** Sequential scalar aggregate queries (like COUNT, SUM) across different tables cause unnecessary database roundtrips and latency.
**Action:** Batch independent aggregate queries into a single database roundtrip by wrapping each aggregate in a `select()` and using `.scalar_subquery().label()` within a single outer `select()` statement, ensuring to use index-based access and provide fallbacks for `None` results like `func.sum()`.
