## 2024-10-24 - JWT Token Verification Flaws
**Vulnerability:** Rate limit bucket poisoning via unverified JWT claims and token revocation bypass due to swallowed HTTPExceptions.
**Learning:** Trusting unverified JWT claims for security controls (like rate limiting) allows spoofing. Broad exception handlers swallow explicit HTTP exceptions, causing fail-open security bypasses.
**Prevention:** Always verify JWT signatures before acting on claims and explicitly catch/re-raise HTTPExceptions before broad exception blocks in security-critical paths.