## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-16 - Eliminate Database Waterfall in Stats Query
**Found:** Three sequential database queries in `get_district_stats` for total districts, population, and active alerts.
**Why it existed:** Simple implementation pattern of counting/aggregating metrics individually, without awareness of latency compounding.
**Fix:** Combined the three separate aggregated metric queries into a single query using SQLAlchemy's `scalar_subquery()`.
**Learning:** When fetching multiple independent aggregate metrics, combine them into a single DB call using `scalar_subquery()` rather than executing sequential I/O operations or using `asyncio.gather` on the same session.
**Watch for:** Other dashboard or analytics endpoints that compute multiple summary statistics with individual `db.execute` calls.
