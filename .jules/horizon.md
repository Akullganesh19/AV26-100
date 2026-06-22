## 2024-05-24 — python-jose to PyJWT Migration
**Risk identified:** python-jose is unmaintained and its dependencies (like cryptography plugins) break often. The jose package itself is not robust against modern security tooling expectations.
**Migration target:** PyJWT, the standard supported library for JWT in Python.
**Migrated this session:** Replaced python-jose with PyJWT in backend dependencies, `deps.py` and `security.py`.
**Remaining:** Full codebase is covered.
**Next session:** Look into `passlib` bcrypt alternatives or other dependencies.
