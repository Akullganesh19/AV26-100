## 2024-11-04 - Authentication Revocation Bypass
**Vulnerability:** Broad exception handler in authentication dependency swallowed HTTPExceptions, causing revoked tokens to be silently validated.
**Learning:** In FastAPI auth dependencies, avoid using broad `except Exception:` blocks around security-critical logic without first catching and explicitly re-raising `HTTPException` to prevent inadvertently swallowing 401 Unauthorized errors.
**Prevention:** Always catch and explicitly re-raise expected `HTTPException`s before a broad `except Exception:` block.
