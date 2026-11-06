## 2026-11-06 - Uncaught HTTPException allows revoked token reuse
**Vulnerability class:** Authentication Bypass / Insecure Revocation
**Entry point:** `backend/app/api/deps.py` in `get_current_user` dependency
**Fix:** Explicitly re-raise `HTTPException` before catching generic `Exception` in token revocation check
**Blast radius before fix:** An attacker could use a revoked (e.g. stolen and flagged) token to access authenticated endpoints, completely bypassing token revocation logic
**Next opportunity:** Audit all `except Exception` blocks in the backend for swallowed security exceptions
