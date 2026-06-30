## 2026-06-30 — Migrate python-jose to PyJWT
**Risk identified:** The `python-jose` library is unmaintained and considered deprecated. It carries security risks and compatibility issues going forward, especially with modern cryptography packages.
**Migration target:** `PyJWT`, which is the standard, actively maintained Python library for JSON Web Tokens.
**Migrated this session:** Replaced `python-jose[cryptography]` with `PyJWT[crypto]` in `requirements.txt`. Updated imports and token decoding/verification options in `backend/app/core/security.py` and `backend/app/api/deps.py` to match `PyJWT` standards, ensuring failure conditions fail closed using `jwt.PyJWTError`.
**Remaining:** None for this specific library replacement. Future sessions might look at other potential legacy library deprecations.
**Next session:** Investigate any other dependencies that have reached end-of-life or are lagging behind major versions.
