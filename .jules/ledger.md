## 2024-05-19 — Race Condition in Simulation Progress
**Value type:** Simulation Current Day (Quota/Count)
**Drift risk found:** Read-then-write on `current_day` in `SimulationService.advance_day` without locking. Concurrent requests could read the same `current_day`, increment it, and write it back, causing lost increments (e.g., 5 requests result in day 2 instead of day 5).
**Fix:** Added pessimistic row-level locking via `.with_for_update()` in SQLAlchemy `select` query before modifying and committing the state.
**Proven by:** Concurrency test `tests/test_simulation_concurrency.py::test_advance_day_concurrency` simulating 5 simultaneous requests. Failed previously with `current_day == 3`, passes now with `current_day == 5`.
**Other balances to check:** `total_rows` incrementing in `IngestionService.run_weather_ingestion` (though mostly single-threaded per pipeline run, could be a risk if pipelines run concurrently for the same target).
