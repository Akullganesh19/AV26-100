## 2024-08-14 — Migrate python-jose to PyJWT
**Risk identified:** `python-jose` is an abandoned library with no ongoing security updates, posing a compounding technical debt risk for core authentication flows.
**Migration target:** `PyJWT`, which is the actively maintained and ecosystem-standard library for JWT handling in Python.
**Migrated this session:** Swapped dependency in `requirements.txt`, updated `deps.py` and `security.py` to use `PyJWT` APIs, fixed `get_unverified_claims` decoding, and updated exception handling to use `jwt.PyJWTError`.
**Remaining:** `passlib` is also outdated and should be migrated to `bcrypt` directly.
**Next session:** Migrate `passlib[bcrypt]` to direct `bcrypt` implementation for password hashing.
