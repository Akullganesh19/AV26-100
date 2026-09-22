## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2023-10-25 - Redundant Pandas DataFrame Sorting Post-SQL Query
**Learning:** Using `.sort_values()` on a Pandas DataFrame is redundant and wastes O(N log N) compute when the underlying SQL query already specifies an `ORDER BY` clause. Boolean filtering on the DataFrame preserves this inherent order, making it safe to directly use `.iloc[0]` for O(1) row access. Additionally, this bypasses `TypeError` issues with `.argmax()` on SQLAlchemy `datetime.date` objects.
**Action:** Always trust the SQL query's sort order when using `ORDER BY`, and replace subsequent Pandas sorting of the same data with direct index access like `.iloc[0]`.
