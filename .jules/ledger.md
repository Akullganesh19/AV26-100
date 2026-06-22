## $(date +%Y-%m-%d) — Simulation Clock Drift
**Value type:** SimulationState `current_day` (a counter/quota representing mission progress)
**Drift risk found:** Read-modify-write race condition. `advance_day` in `SimulationService` fetched the record, incremented `sim.current_day += 1` in memory, and then wrote it back. If an officer rapidly tapped "Advance" or multiple requests hit simultaneously, the `current_day` would only increment by 1 instead of N, causing events meant for Day 2 to fire multiple times or skip entirely, permanently corrupting the mission state.
**Fix:** Added `.with_for_update()` to the `select(SimulationState)` query in `advance_day` and `reset_simulation` to use database row locks, enforcing atomic, serialized execution.
**Proven by:** Concurrency test `test_advance_day_concurrency` simulating 3 parallel advance requests (gathered via `asyncio.gather`), proving `current_day` hits exactly 3, whereas without the lock, it intermittently stopped at 2.
**Other balances to check:** Any other counter logic like API rate limiting, usage tracking, or inventory/budget counters. (None obvious found during initial scan besides `current_day` and basic row counting).
