## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-15 - Batched Scalar Aggregates
**Learning:** Multiple independent scalar aggregate queries (e.g., func.count(), func.sum()) on the same table can be batched into a single select() statement using .label() and .fetchone() to reduce database roundtrips.
**Action:** Always combine aggregate functions on the same table into a single query instead of executing them sequentially.
