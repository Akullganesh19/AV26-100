## 2024-10-11 - Spoofable Rate Limiting via Unverified JWT Claims
**Vulnerability:** The `get_user_id` function extracted the `sub` claim from a JWT without cryptographic verification for rate-limiting.
**Learning:** This allowed an attacker to bypass rate limits by providing a forged JWT with a spoofed `sub` claim.
**Prevention:** Always cryptographically verify JWT claims using `jwt.decode` before using them as identifiers for security controls like rate limiting.
