## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2024-09-24 - O(1) DataFrame row extraction in ml/features.py
**Learning:** For Pandas DataFrame operations, when selecting the first or last row after an SQL query that already orders the results, avoid using `.sort_values()` as it is an O(N log N) operation, and avoid using `.argmax()` on columns containing `datetime.date` objects (like those returned by SQLAlchemy) as it raises a `TypeError`. Since boolean filtering preserves order, if the original dataframe was ordered, the filtered one will be too.
**Action:** Replace `df.sort_values().iloc[0]` with an O(1) `df.iloc[0]` when the underlying dataframe is already sorted by the SQL query.
