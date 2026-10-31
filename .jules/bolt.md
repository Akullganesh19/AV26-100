## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2026-10-31 - [Batch Aggregate Queries]
**Learning:** Three independent scalar aggregate queries in the stats endpoint cause unnecessary database roundtrips.
**Action:** Batched independent scalar aggregates into a single select query with scalar subqueries and used index-based access on the result row to improve performance.
