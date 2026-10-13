## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2026-10-13 - Global Redis Connection Pool for FastAPI Dependencies
**Learning:** Instantiating Redis clients dynamically per request using `redis.from_url()` inside FastAPI dependency functions (like `get_current_user`) creates a new connection pool each time, leading to severe performance degradation and exhaustion of available connections under load.
**Action:** Always define Redis clients globally at the module level when using `redis.from_url()` so the underlying connection pool can be efficiently reused across all requests, and ensure no unintended `await client.aclose()` calls destroy the shared pool.
