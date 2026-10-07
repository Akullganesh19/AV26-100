## 2024-10-07 — Fix Rate-Limiting JWT Spoofing
**Vulnerability class:** Rate-Limit Bypass via JWT Claim Spoofing
**Entry point:** `get_user_id` function in `backend/app/api/deps.py`
**Fix:** Cryptographically verified JWT token using `jwt.decode` before using the `sub` claim for rate limiting.
**Blast radius before fix:** An attacker could bypass rate limits by spoofing `sub` claims, potentially causing denial-of-service by consuming other users' quotas or avoiding ip-based limits.
**Next opportunity:** Review other instances of `get_unverified_claims` to ensure signatures are eventually validated before performing privileged actions.
