## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2023-10-27 — Invalid SQLAlchemy Concurrency
**Found:** Sequential aggregate `db.execute()` calls for `get_district_stats` dashboard stats.
**Why it existed:** Simple implementation pattern of sequential calls in async context without regard for DB latency.
**Fix:** Combined two separate aggregate queries (`COUNT` and `SUM` on `District` table) into a single SQL query (`select(func.count(District.id), func.sum(District.population))`), halving the database overhead for that portion of the API call.
**Learning:** When optimizing sequential database calls in SQLAlchemy using an `AsyncSession`, you cannot simply wrap them in `asyncio.gather` as the underlying async driver (like `asyncpg`) does not support concurrent execution on a single session. This leads to `GreenletError` or connection issues. The correct optimization is to either combine queries or fetch results and process them in-memory.
**Watch for:** Other places where `asyncio.gather` is mistakenly applied to database queries on the same session.
