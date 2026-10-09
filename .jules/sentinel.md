## 2024-05-15 — Exception Swallowing Auth Bypass
**Attacked:** JWT Token Revocation Verification in `backend/app/api/deps.py`
**Found:** A generic `except Exception: pass` swallowed the `HTTPException(401)` meant to reject revoked tokens, falling through to `jwt.decode()`. A mathematically valid revoked token would thus be fully accepted.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added an explicit `except HTTPException: raise` before the generic except.
**Systemic pattern:** Look for `except Exception:` blocks in FastAPI dependency overrides that don't re-raise `HTTPException`.

## 2024-05-15 — Concurrent DB Transaction Corruption
**Attacked:** `predict_batch` in `backend/app/services/prediction_service.py`
**Found:** An `AsyncSession` (`self.db`) was shared across multiple `asyncio.gather` tasks. One task calling `await self.db.commit()` would commit partial/incomplete inserts from all other concurrently running tasks, leading to corrupted transaction isolation and data integrity risks.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Reverted `predict_batch` to sequential iteration since `AsyncSession` isn't thread/task-safe within a single instance.
**Systemic pattern:** Look for `asyncio.gather` or `asyncio.create_task` used in endpoints where a dependency injected `AsyncSession` is passed downstream.

## 2024-05-15 — Background Task GC Mid-Execution
**Attacked:** `asyncio.create_task` in `backend/app/services/prediction_service.py`
**Found:** The `send_alert_notification` background task was created without maintaining a strong reference, meaning the Python event loop's GC could silently destroy it mid-execution.
**Severity:** 🟡
**Fixed or flagged:** Fixed. Maintained a module-level `set()` of strong references.
**Systemic pattern:** Look for `asyncio.create_task` called without assignment to a variable or collection anywhere in the codebase.
