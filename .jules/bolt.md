## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-16 - O(N^2) Window Function Bottleneck & ML Inference on Read Paths
**Found:** Missing `WHERE` clauses inside CTEs defining window functions in SQL, and redundant ML inference runs when fetching jurisdiction matrices.
**Why it existed:** The `lagged_cases` CTE calculated `LAG`/`AVG`/`STDDEV` over the entire `raw_data` table before filtering on `district_id`, causing an O(N^2) DB scan. Similarly, `predict_batch` executed fresh inferences (CPU-bound) for all districts on every `/districts` API call rather than returning already-computed predictions from the database.
**Fix:** Moved the `district_id` and `disease` filter directly inside the CTE before the `WINDOW` definition, turning an entire-table scan into an O(1) indexed lookup scan. Also updated `predict_batch` to first execute a `select(Prediction)` query, caching results and only running inferences for districts missing predictions.
**Learning:** Always apply aggressive filters *before* window functions in SQL to constrain the dataset size. In addition, batch prediction APIs on read paths should prioritize DB lookup first and selectively backfill via CPU/ML inference to reduce heavy compute loads and read latency.
**Watch for:** Other large analytical queries involving `OVER` and `PARTITION BY`, as well as list endpoints running model inferences on the fly.
