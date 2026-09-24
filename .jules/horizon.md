## 2024-09-24 — Migrate python-jose to PyJWT
**Risk identified:** `python-jose` is abandoned, no longer receiving security updates, and has open vulnerabilities. Relying on it for core authentication puts the application at a high security risk that compounds over time.
**Migration target:** `PyJWT`, the actively maintained and standard ecosystem library for JWTs in Python.
**Migrated this session:** Fully replaced `python-jose[cryptography]` with `PyJWT[crypto]` in `requirements.txt` and updated `backend/app/core/security.py` and `backend/app/api/deps.py` to use PyJWT's API natively (using `.decode` with options instead of `get_unverified_claims`).
**Remaining:** The migration of JWT parsing is complete. The next cryptographic dependency risk is `passlib`, which is also unmaintained.
**Next session:** Migrate `passlib` to direct `bcrypt` usage.
