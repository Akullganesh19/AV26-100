## 2025-01-01 — Migrate python-jose to PyJWT
**Risk identified:** `python-jose` is no longer actively maintained, posing a risk for future security vulnerabilities and missing support for newer Python ecosystem features.
**Migration target:** `PyJWT`, which is the standard, actively maintained JWT library in the Python ecosystem.
**Migrated this session:** Replaced `python-jose` with `PyJWT==2.8.0` in `requirements.txt`, updated `deps.py` and `security.py` imports, and transitioned unverified claims decoding and exception handling.
**Remaining:** No remaining work for this specific JWT library migration.
**Next session:** Review other core security dependencies.
