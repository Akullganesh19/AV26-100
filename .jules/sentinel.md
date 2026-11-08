## 2026-06-16 — [Background Tasks GC & DB Cursor Race Condition]
**Attacked:** Prediction batching execution paths in `PredictionService._persist` and `PredictionService.predict_single`
**Found:**
1. `MissingGreenlet`/Cursor invalidation: In `_persist`, `await self.db.commit()` was executed before `result.fetchone()`. In async SQLAlchemy context, `execute()` returns a cursor, and committing the transaction invalidates/closes the cursor. Retrieving the result after committing may lead to unhandled DBAPI errors or MissingGreenlet.
2. Background task garbage collection: `asyncio.create_task` was used in a fire-and-forget manner to trigger alerts without maintaining a strong reference. The Python event loop could garbage collect this task before completion, leading to dropped alerts.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added `background_tasks` set to retain strong references, and reversed the order of `commit()` and `fetchone()` in `_persist`.
**Systemic pattern:** Fire-and-forget tasks using `asyncio.create_task` across the codebase should maintain strong references to avoid premature garbage collection. DB result processing should happen entirely before `commit()`.
