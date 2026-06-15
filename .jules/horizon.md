## 2024-06-15 — Python-JOSE to PyJWT Migration
**Risk identified:** The `python-jose` package is unmaintained (last release in 2021) and the broader Python/FastAPI ecosystem has officially migrated away from it due to lack of updates and underlying cryptographic dependency issues. FastAPI updated its official security documentation to recommend `PyJWT` and `pwdlib`. `passlib` is also effectively abandoned.
**Migration target:** `PyJWT` for JWT handling, which is actively maintained and currently the standard recommendation.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in `requirements.txt`, updated `backend/app/api/deps.py` and `backend/app/core/security.py` to use `PyJWT`'s API syntax (e.g., `jwt.decode(..., options={"verify_signature": False})` instead of `get_unverified_claims`).
**Remaining:** Migrate `passlib` to `pwdlib` or direct `bcrypt` for password hashing, as `passlib` is equally unmaintained.
**Next session:** Replace `passlib[bcrypt]` with `pwdlib[argon2]` or standard `bcrypt` in `backend/app/core/security.py`.
