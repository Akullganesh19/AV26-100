## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2024-05-15 - Combine Independent Scalar Aggregations
**Learning:** Executing multiple independent scalar aggregations (like count and sum) on the same table using separate SQLAlchemy queries results in unnecessary database roundtrips.
**Action:** Combine them into a single `select(func.count(...), func.sum(...))` query to optimize performance without risking `AsyncSession` concurrency issues.
