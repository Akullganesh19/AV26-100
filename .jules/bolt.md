## 2025-05-15 - Concurrent Batch Inference for Jurisdiction Matrix
**Learning:** Sequential async calls in a loop (O(N)) for compute-intensive inference create significant bottlenecks, especially when each call involves I/O and CPU work. Batching these with `asyncio.gather` and a concurrency-limiting semaphore dramatically improves performance.
**Action:** Always prefer `asyncio.gather` with a semaphore for processing multiple independent entities in API routes.
## 2025-05-16 - O(N^2) `.find()` loops during component renders
**Found:** Re-evaluating `array.find()` on every component render inside `SimulationLab.tsx` for nested or repeated elements.
**Why it existed:** Quick implementation logic to search for the active scenario by ID.
**Fix:** Memoized the search logic using `useMemo` so it's calculated only when the source array or lookup ID change.
**Learning:** O(N) searches inside components can impact performance. Always memoize expensive inline array functions if they don't depend on varying render properties.
**Watch for:** Other similar inline `.map()`, `.filter()`, or `.find()` usages in large un-memoized components or loops.
## 2025-05-16 - CI database creation
**Found:** CI job failing with `InvalidCatalogNameError: database "episense_test_test" does not exist`
**Why it existed:** `conftest.py` appends `_test` to the `DATABASE_URL`, resulting in tests querying `episense_test_test` which was missing from the service definition in CI.
**Fix:** Created the `episense_test_test` dynamically before running tests.
**Learning:** Always verify that pytest setups relying on dynamic suffix URLs account for CI environments.
