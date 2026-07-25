## 2024-06-25 — Fixed Authentication Bypass due to Swallowed Revocation Check
**Found:** Broad `except Exception:` block swallowing `HTTPException` in JWT token revocation validation flow.
**Why it existed:** Quick-and-dirty error handling intended to fallback to standard verification if unverified claims extraction failed, without considering that explicit validation exceptions (like 401 on revocation) are also `Exception`s.
**Fix:** Refactored `backend/app/api/deps.py` to specifically catch `HTTPException` (and re-raise), `RedisError` (fail closed with 500), and `JWTError` (continue to normal verification).
**Learning:** Always catch explicit exceptions. When validating credentials against external services (Redis), fail closed on connection errors rather than falling back to potentially bypassing the check.
**Watch for:** Other places where `except Exception:` surrounds validation or authorization blocks.
