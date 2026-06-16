## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2026-06-16 - Frontend Performance Sweep
**Found:** Unnecessary recalculation of static config objects (like stats, chartData, trendData) and Leaflet handlers (styleFeature, onEachFeature) on every render.
**Why it existed:** Variables and functions were instantiated directly inside the React component body without memoization hooks.
**Fix:** Wrapped static array values in `useMemo` and map event handlers in `useCallback` with appropriate dependency arrays.
**Learning:** For continuous-polling dashboards and complex map libraries (Leaflet), recreating props inside the render path significantly increases CPU cycles and causes unnecessary DOM reconciliation.
**Watch for:** Other complex visualizations or real-time polling components that don't memoize their configuration constants.
