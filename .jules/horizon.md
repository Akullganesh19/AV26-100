## 2024-09-04 — Migrate python-jose to PyJWT
**Risk identified:** The `python-jose` library is unmaintained and considered abandoned. Remaining on an abandoned library for authentication tokens presents a major future security risk and technical debt, especially with modernizing dependency stacks.
**Migration target:** PyJWT, which is actively maintained, has comprehensive cryptographic support, and handles JWT standard validations robustly.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in backend dependencies, updating imports and exception handling logic to properly use `jwt.PyJWTError`. Adapted `get_unverified_claims` to use `jwt.decode` with all validations explicitly disabled.
**Remaining:** None for the scope of migrating the core token handling.
**Next session:** Look for other unmaintained or potentially risky cryptographic or third-party logic dependencies to replace.
