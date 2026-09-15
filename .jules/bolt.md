## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-16 - Pandas Sort Overhead
**Learning:** Extracting the latest record from a Pandas DataFrame using `.sort_values().iloc[0]` incurs an O(N log N) sorting overhead, which is a common anti-pattern.
**Action:** Use `.idxmax()` followed by `.loc[]` to achieve the same result in O(N) time without fully sorting the DataFrame.
