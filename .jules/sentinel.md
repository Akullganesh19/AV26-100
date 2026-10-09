## 2025-02-12 - Fix rate limit token spoofing
**Vulnerability:** Unverified JWT claims in rate limiter allowed users to spoof their `sub` identity.
**Learning:** Using `jwt.get_unverified_claims` without a subsequent verification step is dangerous when the extracted data is used for security enforcement (like rate limiting).
**Prevention:** Always use `jwt.decode` to verify cryptographic signatures of JWT tokens before trusting any of their claims, using `jwt.get_unverified_header` first if dynamic algorithm selection is required.
