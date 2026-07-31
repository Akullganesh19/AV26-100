## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-06-12 - Database Filter Pushdown in CTE Window Functions
**Found:** Window functions in CTEs (e.g. `features.py` computing LAG/AVG) were executing over the entire `raw_data` table before filtering by district/disease in the main query, causing a massive O(N²) calculation bottleneck.
**Why it existed:** The `WHERE` clause was applied outside the CTE containing the window functions, leading Postgres to compute windowing for the entire table.
**Fix:** Pushed the `WHERE district_id = :d_id AND disease = :disease` filter into the CTE containing the window function logic.
**Learning:** Always filter as early as possible inside CTEs, especially before expensive window operations or aggregations.
**Watch for:** Other raw SQL queries relying on window functions or heavy aggregations where filters are applied late in the execution plan.

## 2025-06-12 - N+1 Redundant ML Inferences
**Found:** `predict_batch` was blindly dispatching predictions for every district without checking if valid predictions already existed, leading to N+1 redundant ML inferences and DB writes per request.
**Why it existed:** The endpoint was originally designed to force-predict a batch without considering a cache/database persistence layer for recent predictions.
**Fix:** Implemented a single `select` query with `.in_()` to fetch cached predictions for the batch, and only dispatch inference tasks for `missing_district_ids`.
**Learning:** For batch API endpoints, fetch existing data in one query first, and only compute what is missing.
**Watch for:** Other batch-processing endpoints that perform operations independently for each item instead of bulk-checking the database first.
