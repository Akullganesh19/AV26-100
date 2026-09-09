## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2024-05-18 - SQLAlchemy AsyncSession limitations
**Learning:** `asyncio.gather` cannot be safely used to concurrently run database queries on the same SQLAlchemy `AsyncSession` object. The `_db_lock` implementation in the codebase suggests it's not thread-safe.
**Action:** Prefer combining queries at the database level (e.g., using multiple aggregations in a single `select`) rather than running them concurrently in Python when using the same database session.

## 2025-05-18 - CI and DB Names
**Learning:** `conftest.py` adds `_test` to whatever database URL is given. The CI workflow was passing `episense_test` in the URL, causing tests to search for `episense_test_test`, which failed.
**Action:** Changed the init script in the workflow to create `episense_test_test` directly so tests can continue using `episense_test` in the environment URL. This avoids touching the test suite directly.
