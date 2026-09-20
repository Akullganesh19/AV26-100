## 2024-06-15 — PyJWT Migration
**Risk identified:** `python-jose` is abandoned and relies on outdated crypto patterns, posing a long-term security/maintenance risk.
**Migration target:** `PyJWT` which is actively maintained and handles modern token parsing safely.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in dependencies, adapted JWT encode/decode and unverified claims logic in auth middleware (`backend/app/api/deps.py` and `backend/app/core/security.py`).
**Remaining:** None for JWTs.
**Next session:** Look into deprecated SQLAlchemy syntax or other framework deprecations.
