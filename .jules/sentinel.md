## 2024-05-23 - Rate Limit Poisoning and Revocation Bypass
**Vulnerability:** unverified JWT claims for rate-limit buckets, and swallowed HTTPExceptions during token revocation checks.
**Learning:** Exception handling for revocation must preserve HTTP exceptions, and rate limit keys must verify JWTs.
**Prevention:** Decode JWTs synchronously for keys and use except HTTPException: raise.
