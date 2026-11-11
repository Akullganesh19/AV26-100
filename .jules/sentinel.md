## 2026-06-16 — [Auth Bypass via Broad Exception Handling]
**Attacked:** `get_current_user` in `backend/app/api/deps.py`
**Found:** An explicit `HTTPException(401)` meant to reject revoked tokens was swallowed by a broad `except Exception:` block beneath it, allowing revoked tokens to bypass validation.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added `except HTTPException: raise` above the broad exception handler to ensure explicit security rejections are properly propagated.
**Systemic pattern:** Broad `except Exception: pass` patterns swallowing explicit `HTTPException`s. Other dependencies catching exceptions for fallbacks should be reviewed.
