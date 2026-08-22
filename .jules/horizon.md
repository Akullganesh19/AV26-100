## 2024-05-18 — Migrate python-jose to PyJWT

**Risk identified:** python-jose is essentially abandoned, has poor community support, and lacks future security updates. Continuing to use it is a security and maintenance risk.
**Migration target:** PyJWT is actively maintained and is the standard ecosystem choice for handling JSON Web Tokens in Python.
**Migrated this session:**
- Swapped `from jose import jwt` to `import jwt` (PyJWT) in `backend/app/api/deps.py` and `backend/app/core/security.py`.
- Updated `backend/requirements.txt` to replace `python-jose[cryptography]` with `PyJWT[crypto]`.
- Updated PyJWT decode calls to correctly disable verifications during parsing of unverified claims, passing `options={"verify_signature": False, "verify_exp": False, "verify_aud": False, "verify_iss": False}` in place of `jwt.get_unverified_claims`.
**Remaining:**
- Verify if any other files are importing `jose`. `grep -rnw "backend" -e "jose"` showed only these two files and requirements.txt.
**Next session:**
- Keep an eye on any new token verification patterns introduced and ensure they use PyJWT conventions.
