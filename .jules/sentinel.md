## 2024-07-19 — Exception Swallowing & Missing Dual JWT Validation in Auth
**Found:** Broad `except Exception:` blocks in JWT verification logic swallowed `HTTPException`s from token revocation, causing revocation to fail open. Additionally, dual validation for locally generated tokens was absent, leading to `/login` flow tokens being rejected.
**Why it existed:** Likely an attempt to fall through to standard token verification when revocation checks fail, ignoring that `HTTPException` should bypass fall-through.
**Fix:** Split exception handling, specifically caught `JWTError`, `redis.RedisError` to fail closed for infrastructure failures, re-raised `HTTPException`, and added fallback to local HS256 validation if Clerk validation fails.
**Learning:** Always explicitly catch and re-raise or handle `HTTPException` inside broad except blocks when implementing security mechanisms. Dual validation is critical for auth flows issuing local tokens but validating external ones.
**Watch for:** Other areas where `except Exception:` might swallow intended HTTP error responses, especially in middleware or dependency injection (deps.py).

## 2024-07-19 — Privilege Escalation via Mass Assignment in Registration
**Found:** `UserCreate` schema allowed direct assignment of `role` parameter which was passed to `User` object creation in `/register`, enabling users to register as `admin`.
**Why it existed:** Simple mapping from Pydantic schema to SQLAlchemy model using direct assignment without filtering restricted fields.
**Fix:** Hardcoded `role=UserRole.OFFICER` and `is_active=True` during `User` creation in the `/register` endpoint to override user-provided inputs safely.
**Learning:** Never trust client-provided values for privileged fields (like `role`, `is_active`) during entity creation or update, even if defined in a Pydantic schema. Always explicitly assign safe defaults on the server side.
**Watch for:** Any PUT/PATCH endpoints (e.g. `/users/{id}`) that might accept `UserUpdate` payloads and blindly apply all fields without authorization checks.

## 2024-07-19 — Information Leakage in Clinical Exception Handling
**Found:** API endpoints in `clinical.py` returned raw exception strings (`str(e)`) in `HTTPException` details on failure.
**Why it existed:** Convenience for debugging during development, quickly surfacing why model execution or feature validation failed.
**Fix:** Replaced explicit error strings with generic user-facing messages (e.g. `"Clinical screening failed"`) and added structured logging to capture the original exception details and stack trace internally.
**Learning:** Exception details often contain internal system paths, dependencies, or database structures which can be leveraged for reconnaissance. Never reflect raw errors back to the client.
**Watch for:** Other API routes, particularly model inference or external integrations, returning untrusted error strings.
