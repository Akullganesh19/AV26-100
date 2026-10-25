## 2024-10-25 - JWT Spoofing and Revocation Bypass
**Vulnerability:** Unverified JWT claims used for rate limiting allowed spoofing, and broad exception catching swallowed token revocation HTTP exceptions.
**Learning:** Using `jwt.get_unverified_claims` on untrusted input allows trivial bypasses, and broad `except Exception:` blocks around security logic can unintentionally bypass security controls.
**Prevention:** Always synchronously decode and verify JWT signatures before trusting claims, and explicitly catch and re-raise `HTTPException` in dependency chains.
