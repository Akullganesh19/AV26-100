## 2026-11-05 - Broad Exception Blocks Swallowing Security Exceptions
**Vulnerability:** A broad `except Exception:` block in a FastAPI dependency swallowed an `HTTPException` used to block revoked tokens.
**Learning:** In FastAPI auth dependencies, catching broad exceptions can inadvertently swallow explicit `HTTPException`s intended for security control (like 401 Unauthorized), resulting in an authorization bypass.
**Prevention:** Always explicitly catch and re-raise `HTTPException` before a broad `except Exception:` block in security-critical logic.
