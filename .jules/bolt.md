## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2026-11-02 - Batching SQLAlchemy Aggregates
**Learning:** Batching independent scalar queries into a single query using `.scalar_subquery().label()` significantly reduces database roundtrips.
**Action:** Use `.scalar_subquery().label()` and `.fetchone()` with index-based access to batch scalar queries into a single roundtrip.
