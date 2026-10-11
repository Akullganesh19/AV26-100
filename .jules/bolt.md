## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2024-03-24 - Redis Connection Pool Performance
**Learning:** `redis.from_url` in `redis-py` (and `redis.asyncio`) creates a new connection pool by default. Creating it inside FastAPI request dependencies (like `get_current_user`) destroys performance by creating and tearing down a pool per request.
**Action:** Always instantiate Redis connection pools globally (at the module level) and reuse them across requests. Ensure Pydantic `RedisDsn` is cast to a string via `str()` before passing it to `redis.from_url`.
