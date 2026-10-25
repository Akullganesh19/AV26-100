## 2024-10-25 — Fix Rate Limit Bypass and Migrate JWT Library
**Found:** The `limiter` instance in `auth.py` was imported from `app.core.limiter` instead of `app.api.deps`, bypassing the application state limits. Also, the deprecated `python-jose` library was in use.
**Why it existed:** The rate limiter was incorrectly scoped, and the JWT library was outdated.
**Fix:** Pointed the limiter import to the correct module and deleted the unused `app.core.limiter`. Replaced `python-jose` with `PyJWT` across the codebase, correctly ignoring signature validation where unverified claims were expected.
**Learning:** Always ensure limiters are tied to the initialized FastAPI app state to be effective. When changing JWT libraries, explicitly disable claim checks for unverified payloads.
**Watch for:** Other routes importing uninitialized limiters or using legacy cryptography libraries.
