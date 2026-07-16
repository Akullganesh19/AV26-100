## 2026-07-16 — Prevented mass assignment privilege escalation and fixed secure defaults for Auth
**Found:**
1. Mass assignment vulnerability in `/api/auth/register` allowing arbitrary `role` input (e.g. `UserRole.ADMIN`).
2. Authentication failing open when Redis connection error was swallowed in `get_current_user`.
3. Insecure `passlib` library used for password hashing, and incompatible token parsing defaults blocking valid local JWTs.
**Why it existed:**
1. `UserCreate` Pydantic model inherited `UserBase` with a `role` field mapped directly to the ORM user entity.
2. Blanket `except Exception:` block meant to fallthrough to other validation mechanisms was masking actual infrastructure failure.
3. Lack of dual validation mapping for locally generated `HS256` token versus `RS256` Clerk tokens, and reliance on deprecated legacy `passlib` wrappers.
**Fix:**
1. Hardcoded `role=UserRole.OFFICER` and `is_active=True` in `auth.py`.
2. Replaced `passlib` with native `bcrypt` in `requirements.txt` and `security.py`.
3. Added fallback local token validation (HS256) inside `get_current_user` in `deps.py`, and caught explicitly `redis.RedisError` for 500 failsafe instead of swallowing infrastructure failures.
**Learning:**
The auth module heavily relies on multiple sources (Local & Clerk) for tokens. Failing closed upon Redis errors and validating dual token types are required for stability and security. Mass assignments risk privilege escalation in endpoints that dynamically unroll Pydantic models with privileged fields.
**Watch for:**
Any other route where `UserUpdate` or `UserCreate` are dynamically mapped to database models without stripping sensitive properties.
