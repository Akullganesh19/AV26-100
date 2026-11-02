## 2024-05-18 — Sentinel: [Authorization Bypass via Swallowed HTTPException]
**Vulnerability class:** Authorization Bypass
**Entry point:** `backend/app/api/deps.py`
**Fix:** Explicitly catch and re-raise `HTTPException` inside the try/except block around token revocation check to prevent the `except Exception:` block from swallowing `HTTPException` (specifically the 401 Unauthorized for revoked tokens) and incorrectly falling through to standard verification.
**Blast radius before fix:** If a token was revoked, the 401 error raised would be caught by `except Exception`, effectively ignoring the revocation and potentially allowing standard validation to pass, leading to unauthorized access.
**Next opportunity:** Investigate other uses of `except Exception` in security-critical logic.
