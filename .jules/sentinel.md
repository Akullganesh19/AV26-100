## 2026-06-16 — Swallowed HTTPException in get_current_user token revocation check
**Attacked:** `get_current_user` auth dependency in `backend/app/api/deps.py`
**Found:** An explicit `HTTPException(401)` meant to reject revoked tokens is swallowed by a broad `except Exception:` block designed to fall back to standard JWT verification. This means revoked tokens are never actually rejected—they just fall through and get verified as valid.
**Severity:** 🔴
**Fixed or flagged:** Fixed. I will explicitly catch and re-raise `HTTPException` before the broad `except Exception:` block.
**Systemic pattern:** Using broad `except Exception:` to implement fallback logic without re-raising intentional flow-control exceptions (like `HTTPException`). I should check other auth or dependency paths.
