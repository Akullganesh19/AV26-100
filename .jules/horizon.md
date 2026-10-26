## 2024-10-26 — Migrate python-jose to PyJWT
**Risk identified:** `python-jose` is an abandoned library and doesn't get updates.
**Migration target:** `PyJWT` which is maintained and safe.
**Migrated this session:** requirements.txt and backend/app/core/security.py and backend/app/api/deps.py to use `PyJWT`.
**Remaining:** Verify tests and endpoints.
**Next session:** Complete full test coverage.
