## 2026-10-25 - Spoofed JWT Rate Limiting Vulnerability
**Vulnerability:** Unverified token claims used for rate limiting
**Learning:** Relying on unverified claims allows spoofing token identity leading to rate-limiting bucket poisoning
**Prevention:** Synchronously verifying token signatures with the correct keys based on the token's algorithm before using claims
