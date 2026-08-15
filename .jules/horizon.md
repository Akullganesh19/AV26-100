## 2025-02-18 — Migrated from python-jose to PyJWT
**Risk identified:** `python-jose` has been deprecated and abandoned, causing potential security vulnerabilities or integration issues moving forward as JWT standards evolve.
**Migration target:** `PyJWT`, which is actively maintained and is the standard alternative for modern Python applications handling JWTs.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in backend dependencies, updated import statements (`from jose import jwt` to `import jwt`), translated `get_unverified_claims` to `jwt.decode` with correct options, and updated exception handling catching `PyJWTError` instead of generic Exceptions.
**Remaining:** None for token validation in the core authentication dependency file (`deps.py`) and security configuration (`security.py`).
**Next session:** Complete verification for other potential dependencies approaching end-of-life.
