## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2024-05-18 - Reduce DB Roundtrips with Combined Scalar Aggregations
**Learning:** Multiple independent scalar aggregations (like `count` and `sum`) on the same SQLAlchemy model/table can cause multiple database roundtrips. In SQLAlchemy `AsyncSession`, executing them concurrently via `asyncio.gather` is not possible because the session is not thread-safe or coroutine-safe. Doing so leads to an `IllegalStateChangeError`.
**Action:** Combine multiple scalar aggregations into a single `select(func.count(...), func.sum(...))` query rather than executing them as separate roundtrips, avoiding N+1 patterns without risking AsyncSession concurrency issues.
