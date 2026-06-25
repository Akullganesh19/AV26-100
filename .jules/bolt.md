## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-16 - DB Waterfall in Analytics Endpoint
**Found:** Three sequential `await db.execute()` calls for calculating scalar sums/counts in `get_district_stats` (`backend/app/api/routes/districts.py`).
**Why it existed:** It's intuitive to write separate queries for separate logical metrics (total districts, population, alerts). However, this incurs three full database roundtrips.
**Fix:** Combined them into a single query using SQLAlchemy's `scalar_subquery()` and selected them with `.label()`.
**Learning:** Always check analytics and dashboard endpoints for sequential independent queries. If the DB driver isn't concurrent, batch them into a single SQL statement.
**Watch for:** Other `/stats`, `/analytics`, or `/dashboard` endpoints where data is queried sequentially without dependencies.
