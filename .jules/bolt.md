## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2026-10-14 - FastAPI Redis Connection Overhead
**Learning:** Instantiating Redis connections per-request using `redis.from_url()` in FastAPI dependencies bypasses connection pooling, causing severe performance degradation at scale.
**Action:** Use a globally initialized Redis client across the application lifecycle to utilize built-in connection pooling.
## 2026-10-14 - CI Postgres Setup
**Learning:** The GitHub Actions `postgres:15-alpine` service only automatically creates the database named in `POSTGRES_DB`. When tests depend on dynamically generating databases (like appending `_test`), they must be created manually before tests run.
**Action:** Use `createdb` to explicitly create any secondary databases needed by the test suite.
