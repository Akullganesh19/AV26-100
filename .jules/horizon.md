## 2024-06-25 — Migrate python-jose to PyJWT
**Risk identified:** python-jose is no longer actively maintained and the ecosystem is moving away from it. This project relies on it for critical authentication components (JWT issuance and validation), and continuing to use it risks accumulating security vulnerabilities.
**Migration target:** The modern and actively maintained PyJWT library (along with cryptography).
**Migrated this session:** Entirely replaced `python-jose` with `PyJWT==2.8.0` and `cryptography==42.0.5` in the backend requirements and adapted backend authentication code (`backend/app/api/deps.py` and `backend/app/core/security.py`) to the equivalent `jwt.decode` API methods.
**Remaining:** Complete.
**Next session:** Complete.
