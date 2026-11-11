## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2026-11-11 - [Batch Independent Aggregates]
**Learning:** In SQLAlchemy, executing multiple independent aggregate queries across different tables sequentially adds unnecessary latency due to multiple network roundtrips. We can batch them using scalar subqueries wrapped in an outer select statement to execute them in a single database roundtrip without triggering cross-joins.
**Action:** Use `select(select(...).scalar_subquery().label('x'), ...)` and access results via indices (`row[0]`) instead of sequential db.execute calls for multiple stats.
