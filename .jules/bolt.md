## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2024-06-25 — Batch Database Lookup for Prediction Service
**Found:** `predict_batch` method spawning sequential N database reads for missing existing predictions, resulting in N+1 database queries on read paths.
**Why it existed:** The `predict_batch` function wrapped `predict_single` (which checks the DB inherently via conflict resolution but doesn't do a pre-fetch lookup) in `asyncio.gather`.
**Fix:** Extracted read-only cache lookups outside the loop. Added a bulk query `Prediction.district_id.in_(district_ids)` to fetch existing records, and only spawned compute tasks for missing items.
**Learning:** Optimizing batch endpoints that wrap single-resource computations requires extracting existing DB lookups to prevent N+1 queries.
**Watch for:** Other batch endpoints (e.g. `/api/districts` calling batch functions) that might not be fully bulk-optimized.
