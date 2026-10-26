## 2026-10-26 - Rate limiting token validation spoofing
**Vulnerability class:** Unverified JWT claims in rate limiting logic allow bucket poisoning via spoofed tokens.
**Entry point:** Any API route utilizing the Limiter dependency that relies on get_user_id.
**Fix:** Use jwt.decode to synchronously verify token signatures (handling both HS256 and RS256) before trusting claims for the rate limit key.
**Blast radius before fix:** Attackers could bypass rate limits or exhaust another user's rate limit buckets by spoofing the sub claim in the token.
**Next opportunity:** Review other custom dependencies or middleware handling tokens without signature validation.
