## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-16 - Batch Prediction N+1 Query Elimination
**Found:** `predict_batch` recomputed predictions for all districts concurrently instead of checking for existing predictions, leading to redundant DB writes and heavy compute on read paths.
**Why it existed:** The batch prediction endpoint `predict_batch` was wrapping `predict_single` in `asyncio.gather` without a cache lookup outside the loop.
**Fix:** Added a bulk read query (`.in_()`) outside the loop to fetch existing predictions, spawning inference tasks only for missing districts. Overrides correctly bypass this cache.
**Learning:** Always query for existing cached computations in bulk before dropping into an `asyncio.gather` loop for resource-heavy operations to avoid N+1 inference problems.
**Watch for:** Other batch processing loops that might be missing bulk cache lookups outside the loop.
