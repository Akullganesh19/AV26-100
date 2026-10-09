## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2024-05-18 - Optimize Aggregate Queries Database Roundtrips
**Learning:** Multiple aggregate functions on the same table (e.g., `func.count`, `func.sum`) executed sequentially cause unnecessary database roundtrips.
**Action:** Combine them into a single `select()` query to reduce latency and database load.
