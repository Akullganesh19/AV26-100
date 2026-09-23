## 2024-05-20 — Migrate python-jose to PyJWT
**Risk identified:** python-jose is completely unmaintained, has known CVEs and doesn't get updates. Using it for authentication in 2-3 years will be a major security and compliance risk, as well as breaking modern python versions.
**Migration target:** PyJWT[crypto], the industry standard replacement for python-jose.
**Migrated this session:** Swapped python-jose for PyJWT in requirements, updated imports in security and deps, and replaced the deprecated `get_unverified_claims` with `jwt.decode` using unverified options.
**Remaining:** The migration of passlib which is also unmaintained.
**Next session:** Migrate passlib to a modern hashing library like bcrypt directly or argon2-cffi.
