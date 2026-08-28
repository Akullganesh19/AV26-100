## 2024-05-25 — python-jose to PyJWT Migration
**Risk identified:** The python-jose library is abandoned and poses a future security/maintenance risk.
**Migration target:** PyJWT, the active and maintained standard for JWT in Python.
**Migrated this session:** Replaced python-jose with PyJWT across the backend auth system (deps.py and security.py).
**Remaining:** None for this specific dependency.
**Next session:** Investigate other outdated dependencies like passlib.
