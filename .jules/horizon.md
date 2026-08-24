## 2025-03-05 — Migrate python-jose to PyJWT
**Risk identified:** python-jose is abandoned, its dependencies like ecdsa have security vulnerabilities, and it is a risk for future security and maintenance.
**Migration target:** PyJWT is actively maintained and the modern standard for JWT handling in Python.
**Migrated this session:** Replaced python-jose with PyJWT in dependencies, app/api/deps.py, and app/core/security.py. Handled decode method differences and fail-open vulnerability in deps.py.
**Remaining:** None.
**Next session:** Look for other legacy libraries or ecosystem shifts.
