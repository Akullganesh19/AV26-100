## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-15 - Batched Database Aggregations
**Learning:** Performing multiple independent scalar aggregations (like `func.count` and `func.sum`) on the same table as separate database queries causes unnecessary roundtrips and N+1-like performance issues. Combining them into a single `select(func.count(...), func.sum(...))` query reduces database load without risking `AsyncSession` concurrency issues. When dealing with potentially empty tables, always provide a default fallback (e.g., `val if val is not None else 0`), as `func.sum` will evaluate to `None`.
**Action:** Always combine multiple scalar aggregations on the same table into a single query.
