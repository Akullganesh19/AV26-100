## 2026-08-27 — Migrate python-jose to PyJWT
**Risk identified:** `python-jose` is an unmaintained library that will likely break with future cryptography or Python updates.
**Migration target:** `PyJWT`, which is the actively maintained and standard library in the ecosystem.
**Migrated this session:** Fully migrated token encoding and decoding logic in the backend, updated dependencies, and improved exception handling.
**Remaining:** None for this migration.
**Next session:** Evaluate ML dependencies or legacy typing imports.
