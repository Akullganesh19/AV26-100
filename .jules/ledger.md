## 2025-02-15 — Simulation Mission State Race Condition
**Value type:** Current day / mission progress (integer count)
**Drift risk found:** Read-modify-write on `sim.current_day` in `SimulationService.advance_day` with no atomic operation or locking. Concurrent webhook calls or retries would fetch the same day state, increment locally in Python memory, and overwrite, causing events to fire redundantly for the same day offset while failing to progress the mission timeline.
**Fix:** Replaced in-memory increment with an atomic database-level `UPDATE simulation_states SET current_day = current_day + 1 WHERE id = ... RETURNING current_day`.
**Proven by:** Simulated 5 concurrent `advance_day` executions in a custom pytest script (`test_simulation_concurrency.py`). The buggy logic yielded day 2. The patched logic successfully advanced the state to day 5.
**Other balances to check:** `PipelineRun.rows_ingested` in `IngestionService.run_weather_ingestion` is manually aggregated in memory and written at the end, though this is currently safe within a single execution process.
