## 2024-08-24 — Swallowed HTTPException in Token Revocation
**Attacked:** `get_current_user` in `backend/app/api/deps.py`
**Found:** The `except Exception:` block around the Redis token revocation check was catching and suppressing the intentionally raised `HTTPException` (401 Unauthorized), causing revoked tokens to fall through to standard validation and remain valid.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Explicitly caught and re-raised `HTTPException` before the generic exception handler. Added regression tests.
**Systemic pattern:** Broad `except Exception:` blocks used for "fail-open" logic around external services (like Redis) swallowing intentional control-flow exceptions. Look for similar patterns in rate limiting or caching wrappers.
