## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-07-16 — Combine sequential database queries for district stats
**Found:** Three sequential `db.execute` calls for fetching aggregates (total districts, population, active alerts) in the `get_district_stats` endpoint.
**Why it existed:** It was written quickly using straightforward ORM syntax, without considering the database round-trip overhead for each query.
**Fix:** Combined the three queries into a single `db.execute` call using scalar subqueries (`select(func.count(District.id)).scalar_subquery()`).
**Learning:** Sequential DB queries block the async event loop and increase latency. Always combine independent aggregations into a single query using scalar subqueries. Note that `asyncio.gather` cannot be used with `AsyncSession` because it is not thread-safe.
**Watch for:** Other dashboard endpoints or analytics functions performing sequential aggregation queries.
