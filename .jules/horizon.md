## 2024-05-24 — Authentication Dependency Migration
**Risk identified:** The backend uses `passlib` and `python-jose` for authentication. `passlib` is unmaintained and causes runtime crashes (e.g., `AttributeError: module 'bcrypt' has no attribute '__about__'`) with modern bcrypt versions, and `python-jose` is abandoned, compounding technical debt and security risks.
**Migration target:** Native use of the `bcrypt` module for password hashing and verification, and `PyJWT` for standard-compliant JWT creation and verification.
**Migrated this session:** Replaced `passlib` with `bcrypt` in `app/core/security.py` and `python-jose` with `PyJWT` in both `security.py` and `deps.py`. Removed `python-jose` and `passlib` from `requirements.txt`.
**Remaining:** The migration of authentication libraries to `bcrypt` and `PyJWT` is complete for the scope identified.
**Next session:** Look into potential upgrades for other outdated ML dependencies or transition legacy SQL logic if present.
