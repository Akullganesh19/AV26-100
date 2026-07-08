## 2024-07-08 — Migrate away from unmaintained passlib and python-jose
**Risk identified:** `passlib` is unmaintained and relies on the deprecated `crypt` module which is removed in Python 3.13, causing a hard crash for future Python upgrades. `python-jose` is also heavily outdated and unmaintained.
**Migration target:** The modern ecosystem standard is using native `bcrypt` for password hashing and `PyJWT` for JWT decoding/encoding.
**Migrated this session:** Replaced `passlib[bcrypt]` with `bcrypt` and `python-jose` with `PyJWT[crypto]` in `requirements.txt`. Refactored `backend/app/core/security.py` and `backend/app/api/deps.py` to use these new libraries safely.
**Remaining:** None for this specific migration.
**Next session:** Look for other outdated dependencies or legacy patterns (such as fixing the `postgres_where` warning to `postgresql_where` in SQLAlchemy).
