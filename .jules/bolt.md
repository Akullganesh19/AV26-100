## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-16 - Prevent Redis Pool Exhaustion
**Learning:** Instantiating a Redis client per-request (e.g. redis.from_url) creates a new connection pool each time, leading to performance degradation and pool exhaustion under load.
**Action:** Define the Redis client as a global singleton at the module level and reuse it across requests.
