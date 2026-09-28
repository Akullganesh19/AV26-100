## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2024-10-01 - Combining Independent Scalar Aggregations

**Learning:** Combining multiple independent scalar aggregations (like `func.count(...)` and `func.sum(...)`) on the same SQLAlchemy model into a single `select(func.count(...), func.sum(...))` query reduces database roundtrips effectively. This approach avoids the N+1 problem without attempting to execute queries concurrently, which would risk `AsyncSession` `IllegalStateChangeError` since the session is not thread-safe.

**Action:** When aggregating multiple statistics from the same table (e.g., total count, total sum), combine them into a single SQL statement instead of separate ones. This provides a measurable performance improvement for endpoint handlers without concurrency issues.
