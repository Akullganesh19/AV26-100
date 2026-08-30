## 2024-08-30 — Migrate python-jose to PyJWT
**Risk identified:** python-jose is unmaintained and deprecated, creating security and compatibility risks over time.
**Migration target:** PyJWT is actively maintained and the ecosystem standard for JWT handling.
**Migrated this session:** Replaced python-jose with PyJWT in dependencies, app/api/deps.py, and app/core/security.py.
**Remaining:** None. Full migration completed in backend codebase.
**Next session:** Look for other outdated/deprecated libraries or patterns.
