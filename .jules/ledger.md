## 2024-07-06 — Fix simulation mission advance_day concurrency

**Value type:** `SimulationState.current_day` counter (quota/count equivalent)
**Drift risk found:** The snapshot playback engine in `SimulationService.advance_day` incremented `sim.current_day += 1` inside an asynchronous transaction without row-level locking. Concurrent or retried requests would read the same baseline day, causing lost increments and failure to properly advance the simulation state, skipping mission events.
**Fix:** Added pessimistic row-level locking via `.with_for_update()` to the `select(SimulationState)` query.
**Proven by:** The new `backend/tests/test_simulation_concurrency.py` simulates 3 simultaneous requests advancing the day, confirming the final state precisely hits day 3.
**Other balances to check:** Rate limits, API usage quotas, and telemetry counters in `AlertService` or ingestion pipelines should be evaluated.
