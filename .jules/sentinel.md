## 2024-10-05 - Rate Limiting Bypass via Unverified JWT Claims
**Vulnerability:** The rate limiter extracted user IDs from JWT tokens using `jwt.get_unverified_claims(token)` without cryptographically verifying the signature.
**Learning:** Any synchronous function extracting identity from tokens (like `key_func` in `slowapi`) must verify signatures, otherwise attackers can forge claims (like `sub`) to bypass restrictions.
**Prevention:** Always use `jwt.decode` with the appropriate key and algorithm. For multi-tenant setups, check `get_unverified_header` first to route to the correct key.
