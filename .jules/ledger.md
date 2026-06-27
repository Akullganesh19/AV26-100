## 2024-06-27 — Simulation State Drift
**Value type:** Simulation current day (progress tracker)
**Drift risk found:** `SimulationService.advance_day` performs a read-modify-write operation (`sim.current_day += 1`) without any locking mechanism. Concurrent executions would read the same `current_day`, increment it, and overwrite the final state, causing days to be lost in the simulation playback.
**Fix:** Added `.with_for_update()` to the database query selecting the `SimulationState` row, ensuring atomic and serialized access via row-level locks on PostgreSQL.
**Proven by:** Concurrency test `test_concurrent_advance_day` in `backend/tests/test_ledger_simulation.py` firing the same `advance_day` operation simultaneously using multiple database sessions.
**Other balances to check:** Any other mutable state inside `SimulationService` or `AlertService` that follows the same read-modify-write pattern, like `total_days` or risk score computations.
