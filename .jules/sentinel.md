## 2024-07-11 — [CRITICAL] Token Revocation Bypass in get_current_user

**Attacked:** `backend/app/api/deps.py` - `get_current_user` dependency
**Found:** The `try...except Exception` block intended to catch Redis connection errors or JWT parsing errors *also* catches the `HTTPException(401)` explicitly raised when a token is found on the revocation list. The `pass` in the except block causes it to fall through to standard token verification. If the token is cryptographically valid (which it is, it's just revoked), the standard verification succeeds, effectively bypassing token revocation completely.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Will catch specific exceptions (`redis.RedisError`, `jose.exceptions.JWTError`) and allow `HTTPException` to propagate. If Redis fails, we should fail closed (HTTP 500) rather than fail open.
**Systemic pattern:** Look for broad `except Exception:` blocks in authentication/security middleware that might swallow intended explicitly raised exceptions.
