## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-15 — Optimize predict_batch with bulk database cache lookup
**Found:** predict_batch was dispatching predict_single for all districts indiscriminately, causing N+1 DB queries and unnecessary CPU work even for cached items.
**Why it existed:** The async concurrency pattern (asyncio.gather) was implemented, but the read path wasn't extracted from the compute path loop.
**Fix:** Added a bulk SQLAlchemy query to fetch existing Prediction records first. Only missing district_ids are sent through the heavy predict_single path.
**Learning:** When wrapping single-resource computes in asyncio.gather for batch processing, always extract read-only cache lookups outside the loop to prevent N+1 queries.
**Watch for:** Similar patterns in other batch endpoints or scheduled tasks where independent items could be bulk-queried before dispatching tasks.
