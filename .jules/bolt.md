## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-15 - Batch Inference Cache Lookup
**Found:** Batch inference on read paths for jurisdiction matrix performed redundant ML compute and DB writes per district (N+1 bottleneck).
**Why it existed:** The `predict_batch` method delegated entirely to `predict_single` without checking for existing predictions for the same date and model version first.
**Fix:** Extracted a bulk read-only cache lookup using `Prediction.district_id.in_()` outside the loop. Skipped cached entries unless user-supplied overrides were present.
**Learning:** Always batch read-only cache lookups outside of iterative compute functions to prevent N+1 database queries and avoid unnecessary compute on hot paths.
**Watch for:** Other batch processing endpoints wrapping single-resource computations in `asyncio.gather` without a bulk DB fetch first.
