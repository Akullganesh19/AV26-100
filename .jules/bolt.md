## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2024-09-17 - Optimize Feature Builder Date Selection
**Learning:** In Pandas, finding the most recent record by sorting the entire dataframe `df.sort_values(col).iloc[0]` is an $O(N \log N)$ operation which can be slow for large feature sets. Using `df.iloc[df[col].argmax()]` is an $O(N)$ operation that is significantly faster and avoids potential multi-index return issues with `idxmax()` and `.loc[]`.
**Action:** Always prefer `argmax()`/`argmin()` with `.iloc[]` over `sort_values()` when only the single min/max record is required.
