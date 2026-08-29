## 2024-08-29 — python-jose to PyJWT Migration
**Risk identified:** python-jose is abandoned, has unpatched vulnerabilities, and lacks modern security standards updates, making it a growing risk.
**Migration target:** PyJWT, the active and maintained standard for JWT in Python.
**Migrated this session:** Replaced python-jose with PyJWT in backend deps.py and security.py, updating the unverified claims decoding approach.
**Remaining:** None for this specific library, full replacement completed.
**Next session:** Look into outdated pandas/numpy/scikit-learn dependencies.
