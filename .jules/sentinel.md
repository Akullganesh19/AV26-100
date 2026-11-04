## 2024-03-24 - Fix authorization bypass in JWT revocation
**Vulnerability:** Authorization bypass in JWT revocation check due to a broad exception block swallowing the HTTPException(401) intended for revoked tokens.
**Learning:** Broad `except Exception:` blocks around security-critical logic can inadvertently catch and silence intentional security exceptions (like HTTP 401s), causing failure-open scenarios instead of failure-closed.
**Prevention:** Always explicitly catch and re-raise `HTTPException` before a broad exception fallback in authentication dependencies.
