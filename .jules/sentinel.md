## 2026-10-28 — JWT validation bypass and revocation swallowed
**Vulnerability class:** AuthZ Bypass & Exception Swallowing
**Entry point:** Rate limiter (get_user_id) & token revocation (get_current_user)
**Fix:** Verify JWT signatures in get_user_id & re-raise HTTPException in get_current_user
**Blast radius before fix:** Rate limits bypassed by attackers forging tokens; revoked tokens remain valid due to swallowed exceptions
**Next opportunity:** Investigate pagination params or SQL injection points
