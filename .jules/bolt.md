## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2026-11-04 - [Batching Scalar Aggregates]
**Learning:** When batching independent scalar aggregate queries in SQLAlchemy, use scalar_subquery().label() within a single outer select() to avoid multiple database roundtrips or cross-join errors. When extracting values, use index-based access (row[0]) over dynamic attribute access (row.total), and ensure func.sum() has a fallback as it returns None for empty datasets.
**Action:** Always batch multiple simple aggregate queries for performance, and handle None fallbacks properly.
