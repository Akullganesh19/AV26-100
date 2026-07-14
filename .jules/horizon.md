## 2026-07-14 — Remove deprecated passlib
**Risk identified:** `passlib` is deprecated and its standard bcrypt handling relies on the `crypt` module, which is completely removed in Python 3.13. This creates a hard blocker for upgrading the Python version in the future.
**Migration target:** Use the native `bcrypt` library directly for password hashing and verification.
**Migrated this session:** Replaced `passlib[bcrypt]` with `bcrypt` in requirements and updated `verify_password` and `get_password_hash` in `backend/app/core/security.py`.
**Remaining:** Full test pass and deployment to production. No other dependencies on passlib exist.
**Next session:** Monitor error logs post-deployment to ensure all existing password hashes are correctly verified by the raw bcrypt implementation.
