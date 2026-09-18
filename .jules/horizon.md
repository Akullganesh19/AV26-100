## 2024-05-15 — python-jose to PyJWT Migration
**Risk identified:** The `python-jose` library is unmaintained (last release Dec 2020), has unfixed vulnerabilities, and is generally abandoned by the community. As Python and cryptography libraries evolve, it will break.
**Migration target:** `PyJWT`, which is actively maintained, widely used, and supports all modern standards and cryptography versions.
**Migrated this session:** Replaced `python-jose` with `PyJWT` for JWT encoding, decoding, and unverified claim reading in `backend/app/core/security.py` and `backend/app/api/deps.py`. Updated requirements.txt.
**Remaining:** None.
**Next session:** Complete.
