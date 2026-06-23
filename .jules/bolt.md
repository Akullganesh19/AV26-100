## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-15 — Dashboard Stats DB Waterfall
**Found:** Three sequential database queries in `get_district_stats` (`total_districts`, `population_covered`, `active_alerts`) causing a DB waterfall, increasing latency.
**Why it existed:** The `AsyncSession` cannot execute statements concurrently, so `asyncio.gather` could not be used with a single session, leading to sequential awaits.
**Fix:** Combined the three aggregate queries into a single query using SQLAlchemy's `scalar_subquery()` and selecting them as columns, fetching all metrics in a single network round-trip.
**Learning:** Sequential aggregate queries can be combined using `select(q1, q2, q3)` where each `q` is a `scalar_subquery()`, effectively eliminating round-trips without needing concurrent database connections.
**Watch for:** Other endpoints executing sequential scalar aggregations that could be combined into a single query.
