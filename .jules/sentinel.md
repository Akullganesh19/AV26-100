## 2026-06-25 — Fail-Open Token Revocation and Unmaintained Cryptography
**Attacked:** Authentication and token verification paths (`backend/app/api/deps.py`, `backend/app/core/security.py`)
**Found:**
1. The Redis token revocation check used a broad `except Exception:` block that silently passed on infrastructure failure (e.g. Redis down), resulting in a fail-open scenario where a revoked token could be accepted.
2. The authentication logic did not branch its JWT validation logic, failing to cleanly separate RS256 Clerk-issued token verification from HS256 local token verification.
3. The cryptographic dependencies `passlib` and `python-jose` were unmaintained; `passlib` explicitly crashes with an `AttributeError` on modern `bcrypt` versions because it expects `__about__` which has been removed.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Updated `get_current_user` to handle `HTTPException` explicitly and fail closed (HTTP 500) on infrastructure errors. Migrated dependency stack to `PyJWT` and direct `bcrypt` API (`hashpw`/`checkpw`). Branched validation logic on `iss` claim. Verified with regression tests.
**Systemic pattern:** Broad `except Exception:` blocks in critical security paths (like rate limiters, auth middleware, or permission checks). Always inspect try/except blocks around infrastructure calls (DB/Redis) to ensure they fail closed.
