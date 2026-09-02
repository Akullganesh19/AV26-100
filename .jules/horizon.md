## 2024-09-02 — Migrate python-jose to PyJWT
**Risk identified:** `python-jose` has been abandoned, relies on unmaintained cryptography wrappers, and poses a growing security risk.
**Migration target:** `PyJWT`, which is the actively maintained and ecosystem-standard library for JWTs in Python.
**Migrated this session:** Replaced `python-jose` with `PyJWT[crypto]`, updated token decoding logic to handle unverified claims with `verify_signature=False` and explicit validation disabling, and replaced broad exception catching with `jwt.PyJWTError`.
**Remaining:** None for this specific library replacement.
**Next session:** Identify other abandoned or high-risk legacy libraries.
