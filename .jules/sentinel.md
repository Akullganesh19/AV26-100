## 2026-06-25 — Security Sweep: Information Exposure & Insecure Auth
**Found:** Broad exception handling returning `str(e)` in HTTP 500s across API endpoints, token revocation logic catching generic exceptions making it fail-open, and the backend using an unmaintained dependency `python-jose`.
**Why it existed:** Rushed development leading to lazy error handling and reliance on legacy libraries.
**Fix:** Modified exception handling to return generic client errors, explicitly catch `redis.RedisError` in auth flow to fail closed, update internal DB logs to use `type(e).__name__` to not leak internals, and migrate JWT parsing to `PyJWT[crypto]`.
**Learning:** Never catch generic exceptions in security checks, and sanitize all 500-level HTTP exceptions before sending to clients.
**Watch for:** Ensure `python-jose` isn't re-introduced in other services and monitor logs for `jwt.PyJWTError` when JWTs fail.
## 2026-06-25 — [CRITICAL] PyJWT Migration Crash
**Found:** Changing `python-jose` to `PyJWT` without changing the underlying Exception types. The codebase was still relying on legacy Exceptions, which caused tests targeting `tests/ml/test_features.py` to fail, as well as breaking GitHub CI.
**Why it existed:** I didn't update the exception handling across all usages of `jwt.decode`, particularly missing `jwt.PyJWTError`.
**Fix:** Added explicit `except jwt.PyJWTError:` blocks in `backend/app/api/deps.py` and imported `app.models` in `backend/tests/conftest.py` to fix missing table issues.
**Learning:** Always do a full grep for the legacy dependency's error structures when migrating security libraries. Also, CI tests exposed an issue where the database suffix `_test` was appended to the DATABASE_URL, which failed on CI because the test database was named `episense_test`.
**Watch for:** Ensure test configurations in `conftest.py` reflect the environment of the target CI/CD systems.
