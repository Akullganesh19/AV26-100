## 2024-06-18 — Fixing Auth Fail-Open and Information Leakage

**Found:**
1. **Broken Auth Revocation (Fail-Open):** In `backend/app/api/deps.py`, the token revocation check (`get_current_user`) was wrapped in a broad `try...except Exception: pass` block. This meant if the Redis instance storing revoked tokens went down or was unreachable, the exception was swallowed, and the system assumed the token was valid (fail-open).
2. **Information Leakage via Error Handlers:** Multiple endpoints across `backend/app/main.py`, `backend/app/api/routes/districts.py`, `backend/app/api/routes/predict.py`, and `backend/app/api/routes/clinical.py` were catching generic exceptions and returning `str(e)` directly in the HTTP 500 response. This could leak internal system details, database query strings, or stack traces to an attacker.

**Why it existed:**
1. **Fail-Open:** The auth logic prioritized availability over strict security during infrastructure failures, likely to prevent users from being locked out if Redis failed, but this violates the security principle of failing securely (fail-closed).
2. **Information Leakage:** Exposing `str(e)` is often a side-effect of rapid development where developers want to see what broke directly in the API response, rather than checking server logs.

**Fix:**
1. **Auth Revocation:** Modified `backend/app/api/deps.py` to isolate the JWT parsing from the Redis query. If the Redis query fails, it now catches the exception, logs it internally, and explicitly raises an HTTP 500 `Authentication infrastructure unavailable`, ensuring revoked tokens cannot bypass checks during an outage.
2. **Information Leakage:** Replaced all instances of `detail=str(e)` in HTTP 500 exceptions with generic error messages (e.g., "Internal screening error", "Service not ready"). Added internal logging (`logger.error(..., exc_info=True)`) to preserve the stack traces for developers without exposing them to users. In the clinical routes, `str(e)` is still written to the secure database audit log.

**Learning:**
- When working with third-party auth checks or revocation lists, infrastructure failures (like Redis disconnects) MUST result in an access denial (fail-closed) rather than an access grant.
- All HTTP 500 handlers should be audited for `str(e)` or `repr(e)` to ensure internal exception details do not cross the trust boundary.

**Watch for:**
- Other places where external services are queried during authorization or validation steps. If they fail, they must not fail open.
- Future API endpoints being added that catch exceptions and return the raw error message to the client. Always establish a pattern of logging internally and returning generically.
