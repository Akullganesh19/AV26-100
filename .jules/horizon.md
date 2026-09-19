## 2024-05-24 — Migrate from python-jose to PyJWT
**Risk identified:** `python-jose` has been abandoned, posing future security and compatibility risks as Python and cryptography ecosystems evolve.
**Migration target:** `PyJWT`, which is the actively maintained and standard alternative.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in backend dependencies and updated JWT decode/encode flows. Removed insecure unverified JWT claim reading for rate limiting.
**Remaining:** None.
**Next session:** N/A.
