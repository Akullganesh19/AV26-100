## 2024-05-24 - Rate Limit Bypass via Unverified JWT Claims
**Vulnerability:** Rate limiting logic extracted user IDs using `jwt.get_unverified_claims(token)`, allowing attackers to bypass limits by forging tokens with spoofed `sub` claims.
**Learning:** Security mechanisms like rate limiting must always operate on cryptographically verified data, even before full authentication.
**Prevention:** Always use `jwt.decode` with the correct public key and verification options (`verify_aud`, `verify_iss`) to extract user IDs synchronously for rate limiting.
