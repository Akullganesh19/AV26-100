## 2024-06-25 - Rate Limit Authentication Bypass
**Vulnerability:** The rate-limiting middleware (`get_user_id` in `backend/app/api/deps.py`) extracted unverified JWT claims (`jwt.get_unverified_claims`) to determine the user ID.
**Learning:** Rate-limiting keys must be derived from cryptographically verified data. Otherwise, an attacker can trivially spoof the identifier (e.g., the `sub` claim) to bypass per-user rate limits.
**Prevention:** Always verify token signatures using `jwt.decode` (handling appropriate algorithms like HS256 and RS256) before using claims for privileged actions like rate limiting.
