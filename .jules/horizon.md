## 2024-10-24 — Python-Jose to PyJWT Migration
**Risk identified:** The `python-jose` library is unmaintained and its reliance on outdated cryptographic primitives poses a security and maintenance risk. It's a key source of technical debt that will become harder to replace as time goes on and Python ecosystem tools continue to evolve.
**Migration target:** The modern and actively maintained `PyJWT` library, which provides a drop-in replacement for the core JWT decoding and encoding operations.
**Migrated this session:**
- Replaced `python-jose[cryptography]==3.3.0` with `PyJWT[crypto]==2.8.0` in `backend/requirements.txt`
- Updated imports in `backend/app/api/deps.py` and `backend/app/core/security.py`
- Switched `jwt.get_unverified_claims` to `jwt.decode` with signature and claim verification explicitly disabled
- Updated exception handling from generic `Exception` to `jwt.PyJWTError`
**Remaining:**
- The entire transition is effectively complete for the codebase in this session.
**Next session:** Look for other outdated dependencies or legacy patterns.
