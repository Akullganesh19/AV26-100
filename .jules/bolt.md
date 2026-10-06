## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-15 - Combined Scalar Aggregations in SQLAlchemy
**Learning:** Executing multiple independent scalar aggregations (like `func.count` and `func.sum`) on the same SQLAlchemy model as separate queries introduces unnecessary N+1 roundtrips.
**Action:** Combine them into a single `select(func.count(...), func.sum(...))` query to execute all aggregations in one roundtrip without risking AsyncSession concurrency issues.
