## 2026-06-16 — Swallowed HTTPException in Auth Token Revocation Check

**Attacked:** `get_current_user` in `backend/app/api/deps.py`
**Found:** The fail-open token validation logic (checking connection errors to a Redis revocation list) caught `Exception` generically, which inadvertently swallowed `HTTPException` (specifically, the 401 Unauthorized intentionally raised for explicitly revoked tokens).
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added `except HTTPException: raise` before the generic `except Exception:` block to ensure revoked tokens actually raise a 401 error. Also replaced `python-jose` with `PyJWT` because the former is unmaintained and causes validation issues (e.g., `PyJWTError` handling instead of `Exception`), adhering to memory principles.
**Systemic pattern:** Generic `except Exception:` blocks should be reviewed system-wide, particularly in authentication and payment pathways where business logic failures might be incorrectly masked as connection failures.
