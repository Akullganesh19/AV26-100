## 2024-08-13 — Migrate python-jose to PyJWT
**Risk identified:** python-jose is unmaintained and introduces risks around dependency drift and security vulnerabilities for authentication code.
**Migration target:** PyJWT, the actively maintained and standard ecosystem library for JWT.
**Migrated this session:** Swapped python-jose for PyJWT in requirements.txt, replaced get_unverified_claims with jwt.decode(options={'verify_signature': False, 'verify_exp': False, 'verify_aud': False}), updated exception handling from Exception to PyJWTError, and explicitly caught and raised HTTPException in deps.py.
**Remaining:** None for this specific library, the JWT migration is complete.
**Next session:** Start looking for deprecated synchronous dependencies that can be moved to async or evaluate Pydantic v1 vs v2 usages.
