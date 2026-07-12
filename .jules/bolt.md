## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-15 - Batched Dashboard Queries
**Found:** Sequential `await db.execute` calls in `get_district_stats` for aggregate dashboard counts.
**Why it existed:** Simple to write, but creates multiple network roundtrips to the database which degrades performance at scale.
**Fix:** Merged the queries into a single roundtrip using `select(func.count(District.id)).scalar_subquery()`.
**Learning:** For aggregate data, always look for opportunities to combine multiple scalar queries into a single database call. Do NOT use `asyncio.gather` with SQLAlchemy AsyncSessions as they are not thread-safe.
**Watch for:** Other dashboard or reporting endpoints that fetch multiple independent counts.
