## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-15 - Batched Data Fetching in Async Gathering
**Found:** `predict_batch` executed sequential DB select queries inside of the `predict_single` method wrapped by `asyncio.gather`.
**Why it existed:** The `predict_single` method encapsulated the entire feature selection and ML lifecycle, which made it easy to reuse for both single and batch requests, but caused N database trips when called N times concurrently.
**Fix:** Modified `predict_batch` to first execute a single DB query fetching cached baseline predictions across all requested district IDs via `.in_()`, significantly reducing database load on read paths. We only spawn compute/gather tasks for districts not found in the cache.
**Learning:** For batch endpoints hitting endpoints backed by single-resource computation, always extract read-only cache lookups out of the concurrency loop and use SQL `IN` to fetch in bulk before falling back to compute loops.
**Watch for:** Other batch endpoints (like reporting or aggregations) calling single-resource fetchers iteratively instead of batch-fetching.
