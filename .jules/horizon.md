## 2026-08-23 — Migrate python-jose to PyJWT
**Risk identified:** python-jose is abandoned, blocks newer Python versions, and getting harder to maintain over time.
**Migration target:** PyJWT, which is actively maintained and the ecosystem standard.
**Migrated this session:** Replaced python-jose with PyJWT[crypto] in requirements and updated jwt import and get_unverified_claims usages.
**Remaining:** None for this specific migration.
**Next session:** Look for other legacy dependencies to replace.
