## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-16 - Request Coalescing in Frontend API Client
**Found:** Duplicate concurrent API requests due to components mounting and rendering simultaneously (e.g., when navigating complex views or due to rapid state changes), leading to wasted network bandwidth and unnecessary backend load.
**Why it existed:** The frontend used bare `axios.get` calls in various components instead of a centralized `apiClient` that handles request coalescing, causing identical GET requests to fire multiple times if triggered concurrently.
**Fix:** Migrated all component API calls to use a centralized `apiClient` from `frontend/src/api/client.ts` and wrapped `apiClient.get` to cache and return in-flight promises using a `Map`.
**Learning:** Standardize on a central API client and add request coalescing to prevent identical concurrent requests from overwhelming the network and backend.
**Watch for:** Other areas where requests might bypass the `apiClient` or where request coalescing needs a specific cache invalidation strategy.
