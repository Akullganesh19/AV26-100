## 2024-08-20 — JWT Library Migration
**Risk identified:** `python-jose` is unmaintained/abandoned, increasing security risks over time.
**Migration target:** `PyJWT`, the standard and actively maintained library in Python.
**Migrated this session:** Replaced `python-jose` with `PyJWT[crypto]` in dependencies, and migrated token handling in `deps.py` and `security.py`.
**Remaining:** None.
**Next session:** Complete.
