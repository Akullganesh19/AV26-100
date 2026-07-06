1. **Understand the problem**:
   - The Ledger persona dictates that financial/quota/count variables must be consistent and not subject to race conditions.
   - `SimulationService.advance_day` contains `sim.current_day += 1` inside an async function. When called concurrently, multiple requests can read the same `current_day` before the write commits, leading to lost updates. We confirmed this via `test_advance_day_concurrency.py`.
   - The fix is to use SQLAlchemy's `with_for_update()` to pessimisticly lock the row during the advance operation.

2. **Fix `advance_day` in `SimulationService`**:
   - In `backend/app/services/simulation_service.py`, update `advance_day` to acquire a lock using `with_for_update()`.
   - Update: `query = select(SimulationState).where(SimulationState.id == simulation_id).with_for_update()`

3. **Verify the Fix**:
   - Rerun `test_advance_day_concurrency.py`. It should now pass with `final_sim.current_day == 3`.

4. **Document the Fix**:
   - Write to `.jules/ledger.md` using the exact required Ledger format.

5. **Complete pre-commit steps**:
   - Run `pre_commit_instructions` tool to make sure tests, lints and verification are completed.
