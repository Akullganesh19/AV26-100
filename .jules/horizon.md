## 2024-10-24 — Migrate python-jose to PyJWT
**Risk identified:** python-jose is deprecated and not actively maintained, making it a future-proofing and security risk.
**Migration target:** PyJWT, which is actively maintained and standard for JWT handling.
**Migrated this session:** Replaced python-jose with PyJWT across the backend. Updated imports, changed get_unverified_claims to decode with verification flags disabled, and updated exception handling to use PyJWTError. Also patched an exception handling bug in deps.py where HTTPExceptions for revoked tokens were incorrectly swallowed by a bare Exception block.
**Remaining:** None for this specific migration.
**Next session:** Look for other outdated dependencies or patterns to modernize.
