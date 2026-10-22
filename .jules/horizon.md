## 2026-10-22 — python-jose to PyJWT Migration
**Risk identified:** `python-jose` has been deprecated and abandoned. It has unresolved security vulnerabilities and depends on outdated cryptography practices, making it a growing risk as Python and dependencies advance. Relying on an unmaintained security library for authentication in 2026 is an unacceptable risk.
**Migration target:** `PyJWT`, which is actively maintained, the standard in the Python ecosystem for JWT handling, and perfectly compatible with Clerk integrations and our usage patterns.
**Migrated this session:** Replaced `python-jose[cryptography]==3.3.0` with `PyJWT==2.8.0` in `backend/requirements.txt`. Updated import statements from `from jose import jwt` to `import jwt` in `backend/app/core/security.py` and `backend/app/api/deps.py`. Refactored `jwt.get_unverified_claims(token)` to `jwt.decode(token, options={"verify_signature": False})` in `deps.py`.
**Remaining:** Full test suite execution with Postgres to ensure no regressions in auth workflows.
**Next session:** Ensure any frontend/BFF components generating or parsing JWTs are aligned with standard specs.
