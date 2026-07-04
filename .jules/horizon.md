## 2024-07-04 — Migrate jose to PyJWT

**Risk identified:** The backend authentication heavily relied on `python-jose`, which is an unmaintained and deprecated library with potentially unpatched security issues. This is a well-known ecosystem drift risk.
**Migration target:** The modern and actively maintained `PyJWT[crypto]` standard, which seamlessly fulfills the same purpose while being actively patched.
**Migrated this session:**
- `backend/requirements.txt`: Swapped `python-jose[cryptography]==3.3.0` for `PyJWT[crypto]==2.8.0`.
- `backend/app/core/security.py`: Updated imports and usage to standard `jwt` operations.
- `backend/app/api/deps.py`: Migrated dependency injection logic. Specifically, updated the `get_unverified_claims` approach to use `jwt.decode` with full signature/audience verification disabled for strictly pulling out specific fields (e.g. `jti` for Redis revocation checks).
**Remaining:** The migration of `passlib` to `bcrypt` is the next major legacy auth dependency to migrate.
**Next session:** Complete the horizon migration by fully excising `passlib` in favor of direct `bcrypt`.
