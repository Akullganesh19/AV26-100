## 2026-07-03 — Passlib Deprecation Migration
**Risk identified:** The backend currently uses `passlib[bcrypt]` for password hashing, which is unmaintained and poses a compatibility risk with Python 3.12+ due to the `crypt` module deprecation. It was already starting to cause build and runtime issues.
**Migration target:** The modern and maintained ecosystem standard is to use raw `bcrypt` directly for password hashing.
**Migrated this session:** Replaced `passlib.context.CryptContext` with `bcrypt.hashpw` and `bcrypt.checkpw` in `backend/app/core/security.py`. Updated `backend/requirements.txt` to replace `passlib[bcrypt]` with `bcrypt==4.1.3`.
**Remaining:** The migration is fully complete.
**Next session:** Look for other deprecated libraries or APIs, specifically `python-jose` which is mentioned in the memory as a candidate for migration to `PyJWT[crypto]`.