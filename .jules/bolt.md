## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## $(date +%Y-%m-%d) - Code Health Improvement: Removed unused import
**Learning:** Removed `from __future__ import annotations` in `prediction_service.py` as it was unused and bloated the namespace. Verified tests successfully passing locally with mock database instance.
**Action:** Always maintain minimal imports required to reduce memory footprint and prevent circular dependency errors.
