## 2026-07-13 — Privilege Escalation via Mass Assignment in User Registration
**Attacked:** User registration flow (`POST /api/v1/auth/register`)
**Found:** The `UserCreate` schema accepted `role` directly, and the route mapped `user_in.role` to the new user without validation, allowing a normal user to register as `ADMIN`.
**Severity:** 🔴
**Fixed or flagged:** Fixed. I explicitly overrode the role with `UserRole.OFFICER` when instantiating the `User` object in the route.
**Systemic pattern:** Review all endpoints using generic Pydantic schemas (e.g., `UserUpdate`) to ensure fields like `role`, `is_active`, or internal status flags cannot be updated by standard users.

## 2026-07-13 — Token Revocation Bypass & Authentication Fail-Open
**Attacked:** Dependency injection flow for current user (`get_current_user` in `app/api/deps.py`)
**Found:** 1) A broad `except Exception:` block caught the `HTTPException(401)` meant for revoked tokens, bypassing the revocation check. 2) If Redis was unreachable, the same block would swallow the connection error and proceed, causing a fail-open scenario for unverified tokens.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added explicit `except HTTPException: raise`, `except redis.RedisError: raise HTTPException(500)` to fail closed, and let `except Exception:` handle true JWT extraction failures without swallowing business logic errors.
**Systemic pattern:** Look for broad `except Exception:` blocks around critical security, payment, or authorization checks that could inadvertently swallow network errors and fail open.

## 2026-07-13 — Premature Task Cancellation in Alerting
**Attacked:** Prediction single/batch inference alerting flow (`predict_single` in `app/services/prediction_service.py`)
**Found:** `asyncio.create_task` was used to fire-and-forget alerts, but no strong reference was kept. The Python event loop garbage collector could kill these tasks mid-execution.
**Severity:** 🟡
**Fixed or flagged:** Fixed. Added a module-level `_background_tasks = set()` to store task references, attaching `task.add_done_callback(_background_tasks.discard)` to clean them up.
**Systemic pattern:** Check all other locations using `asyncio.create_task` in a fire-and-forget manner to ensure they maintain strong references.
