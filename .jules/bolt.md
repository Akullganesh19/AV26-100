## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-16 - Prevent N+1 compute problem with cached batch lookups
**Found:** `predict_batch` would iterate sequentially or even spawn concurrent requests without first consulting the database for results that had already been processed for identical input configurations (N+1 query problem).
**Why it existed:** The `predict_batch` function did not check the database for pre-computed `Prediction` rows, relying entirely on `predict_single` which executed full feature extraction, DB persistence, and ML models on every single prediction (which are highly redundant for large lists, like dashboards).
**Fix:** Bulk-queried the `Prediction` table for existing predictions using `select(Prediction).where(Prediction.district_id.in_(district_ids))`, and only spawned asynchronous background compute tasks for missing rows (and handled caching bypass for simulation/overrides correctly). Rebuilt output ordering cleanly.
**Learning:** For batch APIs, always pre-load the cache in a single bulk query outside loop iterations rather than relying entirely on individual, lower-level functions querying/writing independent DB records.
**Watch for:** Other batch operations in `app.services` mapping across singletons without pre-fetching data.
