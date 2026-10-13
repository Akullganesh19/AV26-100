## 2024-10-14 - Rate-Limit Bypass via Unverified JWT Claims
**Vulnerability:** The rate limiter extracted the `sub` claim from JWT tokens using `get_unverified_claims` to use as the rate limiting key.
**Learning:** This allowed an attacker to completely bypass rate limiting (such as the 5/minute limit on `/login` and `/register`) by supplying arbitrary, unverified tokens with random `sub` values in each request, causing the limiter to bucket them as different users.
**Prevention:** Never trust unverified JWT headers or claims for access control, rate limiting, or any authorization decisions. Always verify the JWT signature synchronously (e.g., using `jwt.decode` with the proper public or symmetric key) before using any claims from the token.
