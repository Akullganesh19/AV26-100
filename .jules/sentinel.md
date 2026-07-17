## 2024-05-18 — Auth Privilege Escalation & Token Revocation Fail-Open

**Found:** The `auth.py` registration endpoint directly mapped `user_in.role` and `user_in.is_active` fields, allowing Mass Assignment privilege escalation. The `deps.py` token revocation logic incorrectly swallowed `HTTPException` during Redis lookups with a broad `except Exception:` block, bypassing revocation, and failed open when Redis was unavailable. Also, the primary token fallback mechanism was broken because a failed primary verification did not attempt secondary fallback correctly due to broad exception handling that short-circuited the function.

**Why it existed:** Rushed implementation combining third-party auth (Clerk) with local fallback. Convenience over secure defaults for object mapping during registration. Overly broad exception blocks added to prevent 500s from crashing the auth flow unintentionally swallowed explicit security aborts.

**Fix:** Hardcoded safe defaults (`role=UserRole.OFFICER`, `is_active=True`) on registration. In the dependency, updated exception handling to let `HTTPException` propagate, catch `RedisError` to explicitly fail closed (500), and restrict token parsing exceptions to `JWTError` so the dual-auth fallback flow executes properly.

**Learning:** Always use explicit inclusion or exclusion when copying client payload objects to models (never blindly `**user_in.dict()`). Exception handling in auth flows must be tightly scoped; catching base `Exception` is dangerous because it intercepts intentional framework control flow like FastAPI's `HTTPException`.

**Watch for:** Other endpoints parsing `.dict()` directly into SQLAlchemy models without Pydantic exclusions (`exclude={"role", "is_active"}`). Check other background token tasks or rate limiters for "fail open" broad exception swallowing.
