## 2026-06-19 — Simulation Engine Clock Concurrency
**Value type:** Day Quota/Clock (`SimulationState.current_day`)
**Drift risk found:** Read-modify-write without row locking. Concurrent invocations of `SimulationService.advance_day` for the same `simulation_id` would read the same `current_day`, process events for that day multiple times (creating duplicate audit logs and triggering false alerts), and write back the same incremented day, effectively losing clock ticks while multiplying event effects.
**Fix:** Added `with_for_update()` to the `SimulationState` select query in `SimulationService.advance_day` to enforce atomic, serialized access via database row locks.
**Proven by:** `backend/tests/test_simulation_concurrency.py` (`test_concurrent_advance_day` which asserts no duplicate events are processed when two advances execute simultaneously).
**Other balances to check:** `PipelineRun.rows_ingested` aggregation, model metrics evaluation logic if run concurrently.
