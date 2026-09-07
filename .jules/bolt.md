## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2026-09-07 - Unused Imports Code Health
**Learning:** Unused imports like `pickle` in `clinical_service.py` bloat the namespace and can cause confusion.
**Action:** Regularly audit and remove unused imports to improve code readability and maintainability.
