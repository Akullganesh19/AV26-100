## 2026-07-15 — Replace passlib with native bcrypt
**Risk identified:** `passlib` is largely abandoned, relying on the deprecated python `crypt` module which breaks in Python 3.13+. It has not been updated since 2020.
**Migration target:** Native `bcrypt` package directly which handles password hashing and is fully supported in Python 3.12+ and beyond.
**Migrated this session:** Replaced `passlib[bcrypt]` with `bcrypt==5.0.0` in `backend/requirements.txt` and refactored `backend/app/core/security.py` to use `bcrypt.hashpw` and `bcrypt.checkpw`.
**Remaining:** None.
**Next session:** Look for other outdated dependencies or legacy Python 3.9/3.10 constructs.
