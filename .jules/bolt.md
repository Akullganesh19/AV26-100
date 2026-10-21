## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-15 - Global Redis Connection Pool
**Learning:** Creating a new Redis connection pool per request using redis.from_url() in a FastAPI dependency significantly degrades performance and causes resource exhaustion.
**Action:** Always instantiate Redis clients globally at the module level and reuse the connection pool across requests. Avoid calling aclose() on the shared connection.
