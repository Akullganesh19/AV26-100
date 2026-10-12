## 2025-02-12 - Fix unverified JWT claims extraction
**Vulnerability:** The rate limiter `get_user_id` function used `jwt.get_unverified_claims` to extract the user ID without validating the signature.
**Learning:** The function needs to synchronously process rate limits and thus can't use async `Depends` for Clerk configuration. A synchronous signature verification block is needed that conditionally verifies based on the JWT header `alg`.
**Prevention:** Always cryptographically verify JWTs using `jwt.decode` with correct configurations before extracting payload claims for privileged operations like rate limiting.
