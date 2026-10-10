## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2023-10-25 - RedisDsn Type Casting
**Learning:** In the backend, Pydantic URL types like `RedisDsn` (e.g., `settings.CELERY_BROKER_URL`) must be explicitly cast to strings using `str()` before being passed to external libraries like `redis.asyncio` or `redis.ConnectionPool.from_url`, as these libraries expect string arguments and not Pydantic URL objects.
**Action:** Always wrap Pydantic URL types in `str()` when passing them to standard library or third-party functions that expect string URLs.
