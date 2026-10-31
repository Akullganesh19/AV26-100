## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2026-10-30 - Batched DB Scalar Aggregates
**Learning:** Running independent scalar aggregate queries (like `func.count` and `func.sum`) sequentially on the same table incurs unnecessary DB roundtrip latency. Additionally, `func.sum()` returns `None` for empty datasets, requiring an explicit fallback.
**Action:** Batch multiple independent scalar queries on the same table into a single `select()` using `.label()` and `.fetchone()` to cut DB trips in half, and always use `or 0` for `func.sum`.
