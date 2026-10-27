## 2026-10-27 — Token Revocation Bypass
**Vulnerability class:** Authentication Bypass
**Entry point:** backend/app/api/deps.py get_current_user
**Fix:** Catch and explicitly raise HTTPException before generic Exception catch
**Blast radius before fix:** Revoked tokens were completely valid, allowing attackers with compromised tokens to bypass revocation lists.
**Next opportunity:** Audit other authentication middlewares for swallowed HTTPExceptions.
