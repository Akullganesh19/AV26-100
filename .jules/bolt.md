## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.

## 2025-05-15 - Centralize Frontend API Client Usage
**Found:** Several React components (`Dashboard.tsx`, `TacticalAlerts.tsx`, `StrategicMap.tsx`, `DiagnosticsCenter.tsx`, `SimulationLab.tsx`) were bypassing the centralized `apiClient` (`frontend/src/api/client.ts`) and importing `axios` directly for API calls.
**Why it existed:** Likely rapid prototyping where developers imported `axios` directly instead of referencing the configured client, completely bypassing request coalescing and token injection logic.
**Fix:** Replaced all direct `axios` imports and calls with `apiClient`. Removed redundant base URL env variable usage.
**Learning:** When a centralized client with interceptors or request coalescing is present, ensure it's enforced globally. Direct library imports bypass all application-level network optimizations.
**Watch for:** New components being added that revert to importing base `axios` directly instead of the app's `apiClient`.
