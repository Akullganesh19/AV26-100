## 2024-07-01 — Migrate from python-jose to PyJWT
**Risk identified:** `python-jose` is an abandoned library with known vulnerabilities, and the broader Python ecosystem has moved away from it for JWT processing. Relying on it presents a significant security and maintenance risk that will only compound over time.
**Migration target:** `PyJWT[crypto]`, which is actively maintained and the modern standard in the ecosystem for JWT operations.
**Migrated this session:** Replaced `python-jose` with `PyJWT[crypto]` in `backend/requirements.txt`. Updated core security imports and usage of `jwt.decode` in `backend/app/core/security.py` and `backend/app/api/deps.py`, including properly handling token payload extraction and `jwt.PyJWTError` exceptions.
**Remaining:** Completely removing `python-jose` from any other unspotted environments, if any (such as Dockerfiles or CI/CD pipelines if explicitly defined outside `requirements.txt`).
**Next session:** Check if there are other outdated crypto or security libraries needing modern replacements, or confirm Dockerfiles/CI pipelines are pulling the updated requirements seamlessly.
