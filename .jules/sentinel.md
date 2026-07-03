## 2024-05-14 — Authentication Bypass via Exception Swallowing
**Attacked:** `backend/app/api/deps.py` - `get_current_user`
**Found:** Broad `except Exception: pass` block around Redis token revocation check. If Redis is down, or if the `jti` is missing and raises an exception (e.g. from an attacker forging a token), the code silently falls through to standard JWT verification. A revoked token could thus remain valid if the attacker can cause an exception in the revocation check.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Replaced the generic `except Exception` with explicit `except HTTPException: raise` (to allow our 401 out) and `except redis.RedisError: raise HTTPException(status_code=500)` (to fail closed). Added `tests/api/test_deps.py` regression tests.
**Systemic pattern:** Look for other instances of broad `except Exception:` blocks silently continuing or failing open in security-critical paths.
