## 2025-02-28 — Deprecated Cryptography Dependencies Migration
**Risk identified:** The backend authentication relied on `passlib` and `python-jose`. `passlib` is largely unmaintained and fundamentally relies on the Python standard library's `crypt` module which is officially removed in Python 3.13, causing severe compatibility issues going forward. `python-jose` has open security vulnerabilities, is unmaintained, and breaks on newer Python releases.
**Migration target:** Switch directly to `bcrypt` for password hashing and `PyJWT[crypto]` for JSON Web Token issuance and validation. Both are highly active, robust, and the current industry standard.
**Migrated this session:**
- `backend/requirements.txt`: Removed `passlib[bcrypt]` and `python-jose[cryptography]`; added `bcrypt>=4.1.2` and `PyJWT[crypto]>=2.8.0`.
- `backend/app/core/security.py`: Fully transitioned password hashing from `CryptContext` to native `bcrypt` methods and JWT handling to `PyJWT`.
- `backend/app/api/deps.py`: Migrated unverified claims extraction and decoding parameters from `jose` to `PyJWT`.
**Remaining:** No remaining auth cryptography dependencies to migrate for standard JWTs and password hashing in these modules.
**Next session:** Look for other legacy dependencies in Python (like deprecated machine learning tools) or check if Node.js 20 actions in CI workflows are due for upgrade.
