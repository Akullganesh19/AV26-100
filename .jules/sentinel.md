## 2026-06-16 — Auth Revocation Bypass & Batch DB Concurrency & Background Task GC
**Attacked:** Auth token verification logic (`get_current_user`), batch district risk predictions, and background task creation.
**Found:** 1. `get_current_user` swallowed `HTTPException`s from revoked tokens due to a broad `Exception` catch, bypassing revocation checks. 2. `predict_batch` attempted to use `asyncio.gather` on a single `AsyncSession`, causing `IllegalStateChangeError`. 3. Background tasks via `asyncio.create_task` had no strong references and risked silent garbage collection.
**Severity:** 🔴
**Fixed or flagged:** Fixed all three bugs. Re-raised `HTTPException`, changed batch to sequential, and added strong `_background_tasks` tracking.
**Systemic pattern:** Look for `except Exception` swallowing typed exceptions in fail-open auth logic, and check for `asyncio.gather` operating on shared session state anywhere else.
