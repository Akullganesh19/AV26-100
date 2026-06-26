## 2026-06-16 — Token Revocation Bypass Vulnerability
**Attacked:** `get_current_user` in `backend/app/api/deps.py` (Authentication flow)
**Found:** The token revocation check was catching broad `Exception`, meaning if Redis was down or if `jwt.get_unverified_claims` failed, the system would fail open instead of closed. Furthermore, it even caught `HTTPException` thrown by itself, completely negating token revocation.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Replaced broad exception catching with specific exception types and raised a 500 internal server error for infrastructure failures, ensuring fail-closed behavior.
**Systemic pattern:** Look for `except Exception:` blocks in other security, permissions, or billing paths, as they may swallow `HTTPException`s or hide infrastructure failures and result in fail-open behaviors.
