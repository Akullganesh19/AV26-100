## 2025-03-08 — JWT Revocation Check Swallows HTTPException

**Attacked:** `backend/app/api/deps.py` - `get_current_user` function, specifically the token revocation check using Redis.
**Found:** If a token is revoked (found in Redis), the code correctly attempts to raise an `HTTPException(status_code=401)`. However, the entire block is wrapped in a `try...except Exception:` block with a `pass` in the except clause. This means the `HTTPException` is caught and swallowed by the `except Exception:` block, allowing the code execution to fall through and proceed to verify the revoked token normally.
**Severity:** 🔴
**Fixed or flagged:** Fixed. The `except Exception` needs to be more specific or explicitly re-raise `HTTPException`.
**Systemic pattern:** Broad `except Exception: pass` blocks around security or validation logic that contains explicit `raise HTTPException(...)` calls.
