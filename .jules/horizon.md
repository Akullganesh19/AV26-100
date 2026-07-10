## 2025-03-03 — Migrate from passlib to native bcrypt
**Risk identified:** passlib is largely unmaintained and has major compatibility issues with Python 3.12+ due to its reliance on the standard library's `crypt` module which is being deprecated/removed. This will block future upgrades and potentially cause catastrophic authentication failures.
**Migration target:** The native `bcrypt` package, which is actively maintained, directly handles `$2b$` format hashes from existing passwords, and doesn't rely on deprecated Python standard library modules.
**Migrated this session:** Replaced `passlib[bcrypt]` with `bcrypt` in `requirements.txt` and refactored password hashing and verification in `backend/app/core/security.py` to use direct `bcrypt` calls.
**Remaining:** None. This completes the password hashing migration.
**Next session:** Look for other outdated dependencies or legacy patterns (e.g., outdated Node.js versions in CI, or legacy ESLint configs).
