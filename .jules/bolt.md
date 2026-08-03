## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2024-08-03 - Cached Predictions in Batch Inference
**Found:** `predict_batch` always performed full ML inference and database writes for all requested districts, ignoring existing predictions for the same date and model version.
**Why it existed:** The `predict_batch` function was implemented as a simple concurrency wrapper around `predict_single` without checking the database for cached results first.
**Fix:** Modified `predict_batch` to first query the `predictions` table for existing records matching the requested districts, disease, date, and model version. Only missing districts are sent through the heavy inference pipeline.
**Learning:** Always query the database for cached computationally expensive results before spinning up concurrent tasks to recompute them.
**Watch for:** Other batch processing endpoints (like reports or simulations) that might be recomputing identical data unnecessarily.
