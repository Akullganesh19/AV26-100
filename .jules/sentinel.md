## 2026-10-18 — Rate Limit Bucket Poisoning via Unverified Claims
**Vulnerability class:** Authentication Bypass / Rate Limit Evasion
**Entry point:** `get_user_id` rate limiting key function in `backend/app/api/deps.py`
**Fix:** Replaced `jwt.get_unverified_claims` with synchronous `jwt.decode` using `settings` to cryptographically verify token signature before trusting claims.
**Blast radius before fix:** An attacker could craft spoofed JWTs with arbitrary `sub` claims to artificially distribute rate limits across non-existent user IDs, effectively bypassing `slowapi` rate limits and exhausting application resources (e.g. DoS on threads).
**Next opportunity:** Audit other uses of `jwt.get_unverified_claims` (e.g., extracting JTI for Redis revocation checks) to ensure they are not vulnerable to similar spoofing or poisoning attacks.
