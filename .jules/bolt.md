## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-15 - Fast Batch Inference via Bulk DB Select
**Found:** `predict_batch` iterating over models to do full DB checks/writes per-prediction, hitting N+1 bottlenecks.
**Why it existed:** It was wrapping existing single-inference functions blindly.
**Fix:** Introduced bulk read via SQLAlchemy `select().where(district_id.in_(...))` for all pre-cached predictions before batching remaining inferences.
**Learning:** Sequential DB checks wrapped in async loop tasks scale poorly; always fetch cacheable resources upfront in batch.
**Watch for:** Large API routes wrapping singular operations in gather calls without checking cache first.
