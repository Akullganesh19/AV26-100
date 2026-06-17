## 2024-06-17 — Passlib to Bcrypt Migration
**Risk identified:** The backend uses `passlib` to hash passwords. This library is largely abandoned and interacts poorly with modern versions of `bcrypt` (specifically throwing `AttributeError: module 'bcrypt' has no attribute '__about__'`). This blocks local development and updates, creating significant immediate tech debt as dependencies naturally update.
**Migration target:** Move to using direct `bcrypt` API (`bcrypt.hashpw` and `bcrypt.checkpw`) for all backend password hashing and verification.
**Migrated this session:** Replaced `passlib`'s `CryptContext` usage in `backend/app/core/security.py` with direct `bcrypt` calls. Removed `passlib` from `backend/requirements.txt` and pinned `bcrypt==5.0.0`.
**Remaining:** Full codebase sweep to ensure no other obscure modules rely on `passlib`. Review JWT signing/verification to ensure it doesn't need a similarly modernized dependency.
**Next session:** Start by auditing the `python-jose` library usage in `security.py` and `deps.py`, as it also frequently shows its age in the Python ecosystem. Check if migrating to PyJWT is safer.
