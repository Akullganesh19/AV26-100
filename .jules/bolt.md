## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2024-05-18 — Eliminate redundant ML inference and O(N^2) feature extraction bottlenecks
**Found:** `predict_batch` recalculated ML pipelines even for existing predictions, and `FeatureBuilder` calculated `LAG` and `AVG` window functions over the entire dataset before applying district filters. `get_district_stats` made multiple sequential aggregation queries.
**Why it existed:** Suboptimal initial implementation prioritizing feature completeness over scaling and resource efficiency.
**Fix:** Pushed filters down into CTEs before `WINDOW` definitions. Implemented result caching in `predict_batch` by querying existing predictions first. Combined multiple DB aggregations into a single query in `get_district_stats` and fixed a broken query constraint (`Alert.is_resolved`).
**Learning:** Always filter datasets before computing window functions in PostgreSQL. Always check for existing database records before kicking off heavy ML computation pipelines. Aggregate independent metrics in a single query where possible.
**Watch for:** Other batch endpoints missing cache-checks or executing redundant sequential DB queries.
