## 2026-07-09 — passlib to raw bcrypt migration
**Risk identified:** The `passlib` library relies on the Python `crypt` module which is deprecated in Python 3.11 and removed in Python 3.13. As the ecosystem moves forward, relying on `passlib` blocks upgrading Python versions and introduces a brittle dependency on an abandoned package.
**Migration target:** Native `bcrypt` package via `bcrypt.checkpw` and `bcrypt.hashpw` which handles the existing `$2b$` format hashes seamlessly.
**Migrated this session:** Replaced `passlib.context.CryptContext` with native `bcrypt` functions in `backend/app/core/security.py` and updated `backend/requirements.txt` to depend on `bcrypt`.
**Remaining:** None. This component was successfully swapped fully in one piece as it was limited to the core security module.
**Next session:** Look into potential removal of other deprecated Python standard library dependencies or Pydantic v1 to v2 adjustments if any.
