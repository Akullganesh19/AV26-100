## 2024-10-01 - Rate Limit Bypass via Unverified Claims
**Vulnerability:** Rate limiting logic in `deps.py` used `jwt.get_unverified_claims(token)` to extract the user ID for limiting, allowing an attacker to bypass their rate limit or exhaust another user's limit by spoofing the `sub` claim.
**Learning:** Never trust claims from a JWT for any security controls (including rate limiting) without cryptographically verifying the signature first.
**Prevention:** Always use `jwt.decode` with strict signature and audience/issuer verification before extracting claims used for authorization or resource allocation.
