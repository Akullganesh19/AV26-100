## 2024-06-24 — Simulation Engine Drift Fix
**Value type:** SimulationState current_day
**Drift risk found:** Read-modify-write race condition during advance_day
**Fix:** Added with_for_update() row lock
**Proven by:** test_advance_day_concurrency simulation of parallel calls
**Other balances to check:** Alert status mutations and counts
