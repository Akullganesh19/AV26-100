## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Found:** `predict_batch` method ran single inference loops without checking database caches for already existing predictions.
**Why it existed:** It was heavily dependent on asyncio.gather without maximizing cache efficiency.
**Fix:** Modified `predict_batch` to first query `Prediction` for existing records. Now falls back to concurrent operations using asyncio.gather for missing records. Ensures preserving original order.
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance. Adding an upfront bulk read of existing inferences effectively eliminates repetitive heavy ML processing on frequently queried read paths.
**Watch for:** Make sure to explicitly bypass cache functionality if `overrides` are provided to accurately simulate expected impacts in scenario predictions.
