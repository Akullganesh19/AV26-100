## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2026-07-14 — Dashboard Stats Scalar Subquery Refactor
**Found:** Sequential database queries in dashboard stats endpoint (`get_district_stats`), along with an invalid attribute access `is_resolved` on `Alert`.
**Why it existed:** A pattern of straightforward query writing without considering the cumulative latency of multiple trips to the database.
**Fix:** Merged multiple aggregation queries into a single database call using SQLAlchemy scalar subqueries and fixed the Alert status query to correctly check `Alert.status != AlertStatus.RESOLVED`.
**Learning:** Always merge independent aggregations into a single query using scalar subqueries rather than executing them sequentially or with `asyncio.gather` (which breaks AsyncSession).
**Watch for:** Other API endpoints that perform multiple sequential `db.execute()` calls to fetch independent aggregates or metadata instead of merging them via subqueries.
