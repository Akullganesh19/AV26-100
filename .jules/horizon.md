## 2026-07-05 — Authentication Crypto Migration
**Risk identified:** The backend authentication module used `python-jose` for JWT operations and `passlib` (using the deprecated `crypt` module) for password hashing. `python-jose` is unmaintained and causes insecure key warnings, while `passlib` will break in Python 3.13+.
**Migration target:** The modern ecosystem standard is `PyJWT[crypto]` for JWT parsing and generation, and raw `bcrypt` for secure password hashing.
**Migrated this session:** Replaced `passlib` with `bcrypt` in `backend/app/core/security.py` for `get_password_hash` and `verify_password`. Replaced `python-jose` with `PyJWT` in `backend/app/core/security.py` and `backend/app/api/deps.py`. Updated `backend/requirements.txt` to include `PyJWT[crypto]` and `bcrypt`.
**Remaining:** The migration for JWT parsing/generation and password hashing in the backend is complete for the modules identified. Other crypto functions across the backend, if any exist, could be reviewed.
**Next session:** Investigate other potential instances of deprecated crypto or outdated framework usages (e.g. FastAPI/Starlette deprecated patterns).
