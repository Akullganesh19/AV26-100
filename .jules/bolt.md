## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-06-18 - Resolving DB Waterfall with Scalar Subqueries
**Found:** Sequential `await db.execute()` calls in `get_district_stats` created an unnecessary database waterfall, adding latency to the dashboard's initial load.
**Why it existed:** It's intuitive to query each metric separately, but `AsyncSession` doesn't allow `asyncio.gather` for concurrent execution, leaving sequential waits as the default fallback.
**Fix:** Combined the separate aggregate queries into a single query using SQLAlchemy's `scalar_subquery()`, reducing 3 database round-trips to 1.
**Learning:** For aggregated metrics using a single shared database session object, always use a combined query with scalar subqueries rather than relying on sequential awaits.
**Watch for:** Other dashboard endpoints or reporting features that might aggregate data through sequential queries.
