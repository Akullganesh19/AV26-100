## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-18 - DataFrame Argument TypeError with Dates
**Learning:** In pandas, `.argmax()` raises a `TypeError` when called on an `object` dtype column containing `datetime.date` objects returned by SQLAlchemy.
**Action:** When pulling chronological rows ordered by SQL, rely on pandas preserving insertion order during boolean filtering rather than applying sorts or argmax on dates.
