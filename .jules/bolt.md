## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## $(date +%Y-%m-%d) - Optimization of Feature Window Functions and Prediction Caching
**Found:** Performance bottlenecks in SQL feature building where window functions calculated lag/averages over the entire history, combined with redundant, un-cached inferences being re-run continuously for unchanged inputs during batch inference in API routes.
**Why it existed:** CTEs omitted necessary WHERE filters before WINDOW definitions causing O(N^2) complexity execution plans. The batch API generated redundant predictions instead of leveraging previously generated and persisted results.
**Fix:** Pushed down WHERE predicates into the lag/rolling CTE directly, and instituted a look-aside cache in `PredictionService.predict_batch` by querying existing outputs before scheduling background inferences.
**Learning:** Always filter sets before applying DB window functions to bound execution cost. Always cache expensive ML predictions to turn repeat compute workloads into fast I/O lookups.
**Watch for:** Other CTEs running over complete raw datasets or bulk actions circumventing cached states.
