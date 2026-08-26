## 2024-05-18 — python-jose Migration
**Risk identified:** `python-jose` is abandoned, no longer receiving security updates, and becoming a vulnerability risk for future development.
**Migration target:** `PyJWT`, which is actively maintained and the modern standard in Python for JWT parsing and validation.
**Migrated this session:** Swapped `python-jose` for `PyJWT[crypto]` in `backend/requirements.txt` and updated the import statements and specific function calls in `backend/app/api/deps.py` and `backend/app/core/security.py`.
**Remaining:** None.
**Next session:** Complete.
