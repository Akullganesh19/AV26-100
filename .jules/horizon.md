## 2026-09-30 — Migrate python-jose to PyJWT
**Risk identified:** `python-jose` is unmaintained, abandoned, and known to have compatibility issues with modern versions of the `cryptography` library.
**Migration target:** `PyJWT`, which is actively maintained.
**Migrated this session:** Replaced `python-jose` with `PyJWT[crypto]` for JWT handling in `backend/requirements.txt`, `backend/app/api/deps.py`, and `backend/app/core/security.py`.
**Remaining:** The `passlib` hashing library is also unmaintained and should be migrated to `bcrypt` directly.
**Next session:** Migrate `passlib` to `bcrypt` in `backend/app/core/security.py` and `requirements.txt`.
