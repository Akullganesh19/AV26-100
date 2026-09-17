## YYYY-MM-DD — Deprecated python-jose and passlib Migration
**Risk identified:** python-jose and passlib are no longer maintained and have critical bugs in modern environments (e.g. ValueError in passlib on bcrypt >= 4.0, python-jose unmaintained and insecure against newer standards).
**Migration target:** PyJWT for JWT handling, pure bcrypt for password hashing.
**Migrated this session:** Replaced passlib with bcrypt and python-jose with PyJWT in `backend/app/core/security.py` and `backend/app/api/deps.py`. Updated `requirements.txt`.
**Remaining:** Testing full flow with new deps.
**Next session:** Verify authentication end to end.
