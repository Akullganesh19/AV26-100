## 2026-06-25 — Security Sweep: Information Exposure & Insecure Auth
**Found:** Broad exception handling returning `str(e)` in HTTP 500s across API endpoints, token revocation logic catching generic exceptions making it fail-open, and the backend using an unmaintained dependency `python-jose`.
**Why it existed:** Rushed development leading to lazy error handling and reliance on legacy libraries.
**Fix:** Modified exception handling to return generic client errors, explicitly catch `redis.RedisError` in auth flow to fail closed, update internal DB logs to use `type(e).__name__` to not leak internals, and migrate JWT parsing to `PyJWT[crypto]`.
**Learning:** Never catch generic exceptions in security checks, and sanitize all 500-level HTTP exceptions before sending to clients.
**Watch for:** Ensure `python-jose` isn't re-introduced in other services and monitor logs for `jwt.PyJWTError` when JWTs fail.
