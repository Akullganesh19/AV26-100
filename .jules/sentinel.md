## 2026-06-16 — Swallowed Auth Exceptions & Premature DB Commits

**Attacked:** Auth token revocation (`get_current_user`), Prediction persistence (`_persist`)
**Found:**
1. `get_current_user` swallowed `HTTPException` on revoked tokens due to a broad `except Exception: pass`, allowing unauthorized access.
2. `_persist` executed `db.commit()` before `result.fetchone()`, which implicitly closed the cursor on `asyncpg`, leading to a latent `ResourceClosedError` when attempting to fetch the row.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added `except HTTPException: raise` in `deps.py` to prevent explicitly raised auth failures from being swallowed. Swapped the order of `fetchone()` and `commit()` in `prediction_service.py` to correctly consume the result before finalizing the transaction.
**Systemic pattern:** Look out for broad `except Exception:` blocks masking explicitly raised exceptions (especially `HTTPException`), and check all asynchronous database operations using `asyncpg` to ensure results are fetched before `commit()` is called.
