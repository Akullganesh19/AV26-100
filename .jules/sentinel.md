## 2024-06-23 — Token Revocation Bypass and Information Disclosure

**Found:**
1. CRITICAL: The authentication logic (`get_current_user` in `deps.py`) used a broad `except Exception: pass` block when checking the token revocation list in Redis, leading to a fail-open scenario if the Redis infrastructure was down or unreachable. Additionally, it used `jwt.get_unverified_claims`, which could raise exceptions that the code wasn't specifically catching or handling securely.
2. MEDIUM: Several API endpoints (`clinical.py`, `districts.py`, `predict.py`) were directly concatenating or interpolating the raw exception string (`str(e)`) into HTTP 500 error responses, causing information disclosure to clients.

**Why it existed:**
1. The token revocation logic sought to gracefully degrade if the `jti` claim didn't exist or other minor parsing errors happened, but accidentally caught all `Exception`s (like `redis.exceptions.ConnectionError`), allowing revoked tokens to bypass validation when Redis failed.
2. Direct interpolation of exception details is a common debugging pattern during development that was never replaced with secure generic responses and internal logging.

**Fix:**
1. Modified `get_current_user` to catch specific `HTTPException`s explicitly and fail closed on unexpected infrastructure errors. Replaced deprecated `get_unverified_claims` with `jwt.decode(verify_signature=False, verify_exp=False)`.
2. Updated exception blocks across routes to log the error internally using `logger.error(..., exc_info=True)` and return a generic error message in the HTTP 500 response.

**Learning:**
Infrastructure outages (like Redis connection failures) during security checks must fail closed, never fail open. Additionally, always explicitly re-raise expected `HTTPException`s instead of allowing generic exception handlers to swallow them or remap them incorrectly. Generic exception handling is an anti-pattern for security enforcement.

**Watch for:**
Similar fail-open behavior in other security integrations (e.g. rate limiting, CAPTCHAs, or role checkers) where network failures might silently pass the check instead of throwing an error. Also watch out for `str(e)` in error messages being rendered to templates or sent in external APIs.
