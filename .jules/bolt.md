## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2024-10-12 - Redis Connection Pooling Optimization
**Learning:** Dynamically instantiating Redis clients via `redis.from_url` within FastAPI dependency functions (e.g., `get_current_user`) creates a new connection pool for every request, which degrades performance and exhausts connections.
**Action:** Define the Redis client globally at the module level and reuse the shared connection pool across requests.
