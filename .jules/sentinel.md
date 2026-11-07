## 2024-03-22 - [Fix Swallowed HTTPException in get_current_user]
**Vulnerability class:** Authorization bypass
**Entry point:** get_current_user auth dependency
**Fix:** Added explicit catch and re-raise for HTTPException in Redis token revocation check.
**Blast radius before fix:** An attacker could bypass token revocation check and successfully authenticate using a revoked token.
**Next opportunity:** Review other exception handling blocks in security dependencies.
