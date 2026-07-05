## 2024-05-15 — Simulation Day Integrity Fix
**Value type:** Simulation Current Day (Quota/Progress Tracker)
**Drift risk found:** Read-modify-write without pessimistic locking in `SimulationService.advance_day` and `SimulationService.reset_simulation`. If concurrent requests (e.g., retries or double-clicks) attempt to advance the day, the same simulation state could be read, incremented, and written back simultaneously, causing the `current_day` to drift and skip days, missing critical scenario events.
**Fix:** Added pessimistic row-level locking via `.with_for_update()` to the `SimulationState` fetch queries in both `advance_day` and `reset_simulation`.
**Proven by:** Simulated 5 concurrent `advance_day` operations on a single `SimulationState`. Without the lock, the final day was incorrectly recorded as 2. With the lock, the operations serialize properly, yielding the correct final day of 5.
**Other balances to check:** `IngestionService.run_weather_ingestion` (total_rows quota increment) might be at risk if parallel instances run, although it uses an aggregation pattern which is slightly different. Needs future investigation.
