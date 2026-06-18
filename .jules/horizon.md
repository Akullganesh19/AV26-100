## 2026-06-18 — Passlib to Bcrypt Migration
**Risk identified:** `passlib` is unmaintained and causes an `AttributeError: module 'bcrypt' has no attribute '__about__'` when used with modern `bcrypt` versions (e.g. `bcrypt>=4.0.0`). This breaks authentication logic and blocks upgrades.
**Migration target:** Direct usage of the `bcrypt` library API (`bcrypt.hashpw` and `bcrypt.checkpw`) for all local password hashing and verification.
**Migrated this session:** Replaced `passlib` context usage with direct `bcrypt` calls in `backend/app/core/security.py`. Removed `passlib` from `backend/requirements.txt` and added `bcrypt`.
**Remaining:** Tracking down and migrating away from `python-jose`, which is also largely unmaintained, in favor of a modern JWT library (like `PyJWT`).
**Next session:** Migrate JWT creation and verification from `python-jose` to `PyJWT` in `backend/app/core/security.py`.
