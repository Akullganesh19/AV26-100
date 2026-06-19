## 2026-06-19 — Migrate from python-jose to PyJWT

**Risk identified:** The backend `python-jose` dependency for JWT creation and verification is unmaintained, causing potential future security issues and incompatibilities.
**Migration target:** The ecosystem is moving toward `PyJWT` for JWT handling in Python, paired with `cryptography` for RSA keys.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in `requirements.txt`, and updated usage in `app/core/security.py` and `app/api/deps.py`.
**Remaining:** None.
**Next session:** Look for other unmaintained packages or deprecated APIs.
