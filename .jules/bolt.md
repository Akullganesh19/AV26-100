## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2026-06-16 — Frontend Request Coalescing
**Found:** Duplicate, concurrent API requests were not being coalesced, and raw `axios` calls were bypassing the centralized `apiClient` configuration (like Auth headers) across multiple frontend components.
**Why it existed:** The `apiClient` was established in `api/client.ts` but was not consistently used across the application. Furthermore, `apiClient` itself lacked coalescing capabilities.
**Fix:** Refactored `Dashboard`, `StrategicMap`, `SimulationLab`, `DiagnosticsCenter`, and `TacticalAlerts` to import and use `apiClient`. Then, augmented `apiClient.get` with request coalescing logic using a Map to cache promises based on the URL and serialized `config.params`.
**Learning:** Overriding an Axios instance method in TypeScript requires type casting (e.g., `as typeof originalGet`), and `config.params` can be instances of `URLSearchParams` which require specific extraction logic to serialize properly.
**Watch for:** Future components making raw `axios` calls instead of using `apiClient`.
