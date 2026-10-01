## 2026-10-01 — Migrate from python-jose to PyJWT
**Risk identified:** The `python-jose` library is abandoned and causes integration headaches (especially with dependency conflicts). It introduces security risk over time as vulnerabilities are left unpatched.
**Migration target:** The modern standard is `PyJWT`, which is actively maintained, well-supported, and standard for JWT handling in Python projects.
**Migrated this session:** Replace `python-jose` with `PyJWT[crypto]` in `backend/app/api/deps.py` and `backend/app/core/security.py`, and update `backend/requirements.txt`.
**Remaining:** Migrate `passlib` to modern `bcrypt` / `argon2` directly, but that's for next session.
**Next session:** Investigate `passlib` alternatives for modern password hashing to eliminate the final unmaintained crypto dependency.
