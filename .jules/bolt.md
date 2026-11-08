## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-15 - Batched Aggregate Queries
**Learning:** Sequential independent aggregate queries against different tables cause unnecessary database roundtrips, increasing latency. While `asyncio.gather` cannot be used safely with a single SQLAlchemy `AsyncSession` due to concurrency restrictions, we can batch them into a single database roundtrip using nested `select().scalar_subquery().label()` statements.
**Action:** Always batch multiple independent scalar queries into a single outer `select()` query using `scalar_subquery()` when reading multiple disparate metrics for dashboards.
