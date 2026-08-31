## 2024-08-31 — Migrate python-jose to PyJWT
**Risk identified:** `python-jose` is an abandoned library with known security vulnerabilities (e.g., CVE-2024-33663). It is deeply embedded in the authentication flow and poses an escalating security risk as the ecosystem moves away from it.
**Migration target:** `PyJWT`, which is actively maintained, widely adopted, and the settled ecosystem standard for JWT handling in Python.
**Migrated this session:** Replaced `python-jose` with `PyJWT[crypto]==2.8.0` in `requirements.txt`, updated `backend/app/api/deps.py` and `backend/app/core/security.py` to use `import jwt` instead of `from jose import jwt`. Updated unverified claim extraction to explicitly disable all validations and replaced generic exception handling with `jwt.PyJWTError` and explicit `HTTPException` re-raising.
**Remaining:** Full migration of JWT handling completed this session. No remaining tasks.
**Next session:** Look into upgrading other outdated dependencies like `passlib` if they present a future risk.
