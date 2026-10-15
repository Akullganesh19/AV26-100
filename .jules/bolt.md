## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2024-06-25 - Avoid per-request Redis connection pools in FastAPI
**Learning:** Instantiating `redis.from_url()` dynamically inside FastAPI dependency functions (e.g., `get_current_user`) is a severe anti-pattern because it creates and tears down a new connection pool on every request, degrading performance under load.
**Action:** Always define the `redis.asyncio` client globally at the module level (e.g., `redis_client = redis.from_url(...)`) and reuse it across requests to leverage built-in connection pooling. Remove any `await r.aclose()` calls in request paths to prevent prematurely closing the shared pool.
