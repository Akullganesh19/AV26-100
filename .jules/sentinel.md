## 2026-06-16 — Swallowed HTTPException in Token Validation
**Attacked:** Token validation logic in `backend/app/api/deps.py` (`get_current_user`).
**Found:** The fail-open logic for checking the Redis revocation list used a broad `except Exception:` block that swallowed the intentionally raised `HTTPException` (401) when a token was explicitly revoked. This allowed revoked tokens to fall through to standard validation and be accepted if their signature was valid.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added an explicit `except HTTPException: raise` before the generic exception handler, and added a regression test in `backend/tests/test_deps_auth.py`.
**Systemic pattern:** Look for other `except Exception:` blocks that might swallow HTTP-level control flow exceptions (e.g., in other dependencies or background tasks).
