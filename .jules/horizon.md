## 2024-05-20 — python-jose to PyJWT Migration
**Risk identified:** python-jose is unmaintained and effectively abandoned, posing a long-term risk for security vulnerabilities in JWT parsing and verification.
**Migration target:** PyJWT, which is the actively maintained and ecosystem-standard library for JWTs in Python.
**Migrated this session:** Fully migrated dependency from python-jose to PyJWT, including updating all `get_unverified_claims` and `.decode` usages.
**Remaining:** None. Full migration of the dependency is complete.
**Next session:** Look for other outdated dependencies or frameworks.
