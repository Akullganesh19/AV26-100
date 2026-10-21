## 2024-05-24 - Rate Limit Poisoning via Unverified JWT Claims
**Vulnerability:** Rate limiting used `get_unverified_claims` allowing bucket poisoning via spoofed tokens.
**Learning:** Rate limiter keys require synchronous extraction, but bypassing signature verification allows clients to exhaust quotas of other users.
**Prevention:** Use `get_unverified_header` to inspect algorithms, then perform full synchronous signature verification before extracting rate limit identifiers.
