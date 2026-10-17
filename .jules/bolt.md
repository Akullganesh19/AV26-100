## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2026-10-17 - Global Redis Connection Pool for FastAPI Dependencies
**Learning:** Instantiating `redis.asyncio` clients via `redis.from_url()` per-request within FastAPI dependency functions (e.g., `get_current_user`) creates a new connection pool for every request, which degrades performance and can lead to connection exhaustion.
**Action:** Always instantiate Redis clients globally at the module level and reuse them across requests in FastAPI dependencies. Additionally, when refactoring to a shared pool, ensure any associated `await client.aclose()` calls are removed to prevent closing the shared connection.
