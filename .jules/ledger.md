## 2026-06-29 — Race Condition in SimulationState Day Advancement
**Value type:** SimulationState `current_day` (quota/usage counter for simulation progression)
**Drift risk found:** Read-modify-write without row locks on `current_day += 1`. Concurrent requests to `advance_day` would read the same `current_day`, increment it locally, and write back the same value, silently swallowing one or more "advancements" and losing days in the scenario playback.
**Fix:** Added `.with_for_update()` to the `SimulationState` SELECT query in `SimulationService.advance_day` to enforce a row-level lock and ensure atomic, serialized increments.
**Proven by:** Concurrency test `test_simulation_concurrent_advance_day` which asserts `current_day == 2` after firing two asynchronous `advance_day` calls concurrently.
**Other balances to check:** Any other counters or aggregated stats (e.g., in `PipelineRun` stats or `ModelMetric` updates).
