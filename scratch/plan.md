1. **Optimize CTE in `backend/app/ml/features.py`**
   - Add a `WHERE district_id = :d_id AND disease = :disease` filter inside the `lagged_cases` CTE.
   - Run `python3 -m py_compile backend/app/ml/features.py` to verify syntax.
   - Run `cat backend/app/ml/features.py` to verify the write.

2. **Fix Background Task Garbage Collection and Caching in `predict_batch`**
   - In `backend/app/services/prediction_service.py`, declare a module-level `_background_tasks = set()`.
   - In `predict_single`, maintain a strong reference by adding `task = asyncio.create_task(...)` to the set and appending `.add_done_callback(_background_tasks.discard)`.
   - In `predict_batch`, add database caching: Fetch existing predictions for the requested `district_ids`, `disease`, `as_of_date`, and `model_version` via a `select(Prediction).where(...)` query. Avoid calling `predict_single` for IDs that already exist. This is the main performance fix for N+1 queries.
   - Add `from sqlalchemy import select` at the top of the file to support the query.
   - Run `python3 -m py_compile backend/app/services/prediction_service.py` to verify syntax.
   - Run `cat backend/app/services/prediction_service.py` to verify the write.

3. **Run Backend Tests**
   - Execute `cd backend && PYTHONPATH=. pytest tests/ -v` to ensure no regressions.

4. **Complete pre-commit steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

5. **Submit the PR**
   - Submit the changes using the submit tool.
