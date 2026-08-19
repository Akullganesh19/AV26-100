## 2024-08-19 — JWT Dependency Migration
**Risk identified:** python-jose is an abandoned dependency, posing security and maintenance risks.
**Migration target:** PyJWT, which is actively maintained and standard for Python JWT handling.
**Migrated this session:** Replaced python-jose with PyJWT in the backend, updating requirements, token decoding options (disabling signature, exp, and aud verification for unverified claims), and exception handling (PyJWTError).
**Remaining:** None for this specific migration.
**Next session:** Evaluate other lagging dependencies.
