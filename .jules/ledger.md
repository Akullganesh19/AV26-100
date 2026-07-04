## 2025-03-02 — Simulation Clock State Drift Fix
**Value type:** Simulation clock / current_day quota count
**Drift risk found:** Read-modify-write on `current_day` in `SimulationService.advance_day` without database locking. Under concurrent simulation advance requests, multiple threads could read the same `current_day` value and overwrite it to the same increment, causing the mission timeline quota to drift behind actual played steps.
**Fix:** Applied pessimistic row-level locking via `.with_for_update()` in the SQLAlchemy `select()` query for `SimulationState`. This ensures atomic read-increment-commit operations, queuing concurrent requests until the lock is released.
**Proven by:** Simulated 5 concurrent `advance_day` operations via `asyncio.gather`. The failing test resulted in `current_day=1` instead of `5`. Post-fix, the test predictably verifies `current_day=5` across parallel advances.
**Other balances to check:** Any other mutable integer quotas/counters in the codebase, such as `user_alert_thresholds` or `pipeline_run.rows_ingested`, although simulation progress represents the most immediate concurrency risk given its interactive event-driven nature.
