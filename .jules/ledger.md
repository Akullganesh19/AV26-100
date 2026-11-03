## 2024-11-03 — Simulation Event Duplication Risk
**Value type:** Simulation clock and triggered events (e.g. audits, alerts)
**Drift risk found:** `SimulationService.advance_day` used a read-modify-write pattern on the simulation clock without locking. Concurrent requests could read the same day, increment it simultaneously, and duplicate all day-offset events (like generating 18 risk audits instead of 6).
**Fix:** Added database-level row locking with `with_for_update()` on the `SimulationState` query.
**Proven by:** Code analysis showing a classic read-modify-write race condition without a transaction lock, which allows concurrent day advancements.
**Other balances to check:** Any other time-based progression logic that might use non-atomic read-modify-write.
