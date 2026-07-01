## 2026-07-01 — Fix Simulation Clock Race Condition
**Value type:** Simulation clock `current_day` (behaves as a state counter)
**Drift risk found:** The snapshot playback engine (`advance_day` in `SimulationService`) reads `current_day`, increments it in memory, and writes it back without atomicity. Rapid, concurrent clicks (or API requests) read the same `current_day`, triggering identical side-effects (e.g. creating `PredictionAuditLog` and generating alerts) and skipping time progression.
**Fix:** Applied row-level locking via `.with_for_update()` to the `SimulationState` fetch. This ensures exactly one concurrent API request can evaluate and increment the clock at a time.
**Proven by:** Concurrency test `backend/tests/test_simulation_race_condition.py` which fires 3 concurrent API actions and confirms the clock cleanly advances exactly 3 days and events are correctly generated.
**Other balances to check:** None remaining within `SimulationService`.
