## 2024-09-01 — Replace python-jose with PyJWT
**Risk identified:** `python-jose` is abandoned, hasn't received updates in years, and poses a security risk for modern cryptographic standards.
**Migration target:** `PyJWT` which is actively maintained and the ecosystem standard.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in `requirements.txt`, updated `deps.py` and `security.py` to use `PyJWT` for token decoding and verification.
**Remaining:** Ensure other microservices or frontend tools don't rely on `python-jose` specific token structures if any exist.
**Next session:** Migrate `passlib` to modern `bcrypt` directly.
