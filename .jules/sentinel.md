## 2024-10-21 - Authentication Bypass & Rate Limit Spoofing
**Vulnerability:** Attackers could evade rate limits by spoofing tokens or use revoked tokens indefinitely.
**Learning:** Broad exception handling in `get_current_user` swallowed the 401 when tokens were revoked, and `get_user_id` blindly trusted claims without verification.
**Prevention:** Explicitly raise `HTTPException` in the try block and synchronously verify token signatures in the rate-limiter before trusting the `sub` claim. Also instantiate Redis globally to avoid performance degradation.
