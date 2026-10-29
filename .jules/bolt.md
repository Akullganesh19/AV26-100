## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-15 - Batching Independent Scalar Queries
**Learning:** Executing independent scalar aggregate queries (like func.count and func.sum) sequentially on the same table incurs unnecessary database roundtrips. Batching them into a single select() statement with labels reduces I/O latency.
**Action:** Batch multiple independent scalar aggregates on the same table into a single query using .label() and .fetchone() to reduce roundtrips. Handle None returns for func.sum() explicitly.
