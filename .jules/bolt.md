## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2026-11-01 - [Batch Independent Aggregates]
**Learning:** Independent scalar aggregate queries on different tables can be batched into a single database roundtrip using `select(..., ..., ...)` with `.scalar_subquery().label()` to reduce latency.
**Action:** Use this technique when computing multiple dashboard metrics concurrently to avoid N+1-like performance issues.
