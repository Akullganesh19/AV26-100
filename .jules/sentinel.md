## 2024-05-24 - Rate Limit Bucket Poisoning
**Vulnerability:** `get_user_id` used `jwt.get_unverified_claims` to extract user ID for rate limiting, allowing spoofed tokens to poison other users' rate limit buckets.
**Learning:** `slowapi` key_func must be synchronous, leading to the use of unverified claims as a shortcut instead of synchronous decoding.
**Prevention:** Always verify token signatures synchronously before using claims for security controls, checking `jwt.get_unverified_header` to choose the correct public/private key.
