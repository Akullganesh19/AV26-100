## 2024-10-19 - JWT Spoofing and Exception Handling Bypass
**Vulnerability:** Rate limiting bypass via JWT signature spoofing using `jwt.get_unverified_claims`, and blocklist bypass where revoked token `HTTPException`s were swallowed by a broad `except Exception:` block.
**Learning:** Never trust unverified claims even for pre-flight operations like rate limiting key generation. Also, broad exception handlers around security logic can unintentionally silently fail-open, nullifying security controls.
**Prevention:** Always verify token signatures (`jwt.decode`) synchronously if local, explicitly falling back if unverified. Additionally, strictly scope exception handling to avoid catching explicitly raised `HTTPException`s that signify authentication/authorization failures.
