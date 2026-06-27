## 2024-06-27 — Migrating python-jose to PyJWT
**Risk identified:** The `python-jose` library is unmaintained and heavily dependent on outdated cryptography packages, which presents an increasing security vulnerability and maintenance headache as the Python ecosystem continues to evolve.
**Migration target:** `PyJWT[crypto]`, which is the actively maintained and widely adopted standard for JWT management in the modern Python ecosystem.
**Migrated this session:**
- Swapped `python-jose[cryptography]` for `PyJWT[crypto]` in `backend/requirements.txt`.
- Replaced `from jose import jwt` with `import jwt` in `backend/app/api/deps.py` and `backend/app/core/security.py`.
- Replaced `jwt.get_unverified_claims` with `jwt.decode` (using options flags for bypassing signature verification) in `backend/app/api/deps.py`.
- Updated exception handling from general `Exception` to `jwt.PyJWTError`.
**Remaining:** Full test suite execution and validation of other environments (e.g. CI/CD or dockerization) that rely on `requirements.txt`.
**Next session:** Complete full backend test execution, run pre-commit checks, and submit PR to formalize the migration.
