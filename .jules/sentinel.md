## 2024-10-04 - Fix JWT unverified claims spoofing vulnerability
**Vulnerability:** Use of `jwt.get_unverified_claims` allowed attackers to bypass authentication and rate limiting by spoofing claims.
**Learning:** Always cryptographically verify JWTs before reading claims (like `sub` or `jti`) to prevent attackers from injecting arbitrary data into security-critical flows (e.g. rate limiting or token revocation).
**Prevention:** Use `jwt.decode` with correct keys and algorithms instead of `jwt.get_unverified_claims`.
