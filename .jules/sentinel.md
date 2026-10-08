## 2024-10-08 - JWT Auth bypass in rate limiting
**Vulnerability class:** Authentication bypass / Spoofing
**Entry point:** `backend/app/api/deps.py` `get_user_id` rate limiting key_func
**Fix:** Cryptographically verify the token signature and handle multiple algorithms before extracting rate-limiting claims.
**Blast radius before fix:** An attacker could easily forge tokens to bypass user-specific rate limits and flood the system or exhaust shared rate-limit buckets.
**Next opportunity:** Investigate where `get_unverified_claims` or unverified headers are used and potentially trusted.
