## 2026-07-02 — Simulation Clock Concurrency Drift

**Value type:** Simulation clock state (`current_day` in `SimulationState`)
**Drift risk found:** Read-modify-write on `sim.current_day += 1` inside `advance_day()` with no locking. If executed concurrently (e.g. from double-click or replay), the clock misses an advancement, resulting in duplicate injected scenario events for the same day (such as duplicate clusters and pseudo-alerts), breaking simulation integrity.
**Fix:** Added `.with_for_update()` to the `SimulationState` fetch to apply a pessimistic row-level lock in the database.
**Proven by:** Concurrency test `test_advance_day_concurrency` confirming two simultaneous executions now result in `current_day == 2` instead of 1.
**Other balances to check:** Any other counters incremented directly (e.g., metric aggregates or usage limiters) should be reviewed for similar unprotected read-then-write updates.
