## 2026-11-03 - [CRITICAL] Fix authorization bypass for revoked JWTs
**Vulnerability:** The broad `except Exception:` block in the FastAPI auth dependency swallowed `HTTPException`s raised during token revocation checks.
**Learning:** Always catch and explicitly re-raise framework-specific exceptions like `HTTPException` when using broad exception handlers in security-critical paths.
**Prevention:** Avoid blanket exception handlers around auth validation; if necessary, ensure expected flow-control exceptions are explicitly allowed to bubble up.
