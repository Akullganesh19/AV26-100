## 2024-10-17 - [Rate Limit Bucket Poisoning via Spoofed Tokens]
**Vulnerability class:** Rate Limiting Bypass / Bucket Poisoning
**Entry point:** `get_user_id` in `backend/app/api/deps.py` used by `slowapi` limiter.
**Fix:** Replaced `jwt.get_unverified_claims` with synchronous `jwt.decode` using either Clerk public key (RS256) or internal secret key (HS256) based on the unverified header.
**Blast radius before fix:** An attacker could craft a spoofed JWT with an arbitrary `sub` claim and send numerous requests. The unverified claim would be parsed and used as the rate limit key, effectively bypassing the rate limit for the actual attacker while potentially locking out legitimate users (bucket poisoning).
**Next opportunity:** Check for other instances where unverified claims or headers are trusted, such as in telemetry or asynchronous task queuing.
