## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-15 - Concurrent SQLAlchemy AsyncSession queries
**Learning:** SQLAlchemy `AsyncSession` is not thread-safe or coroutine-safe. Attempting to use `asyncio.gather` to execute multiple queries concurrently on the same session object will cause an `IllegalStateChangeError` and crash the application.
**Action:** When trying to optimize multiple independent queries in an API route, either combine them into a single SQL query (e.g., passing multiple aggregate functions to `select()`), or execute them sequentially. Do not use `asyncio.gather` with a shared DB session.
