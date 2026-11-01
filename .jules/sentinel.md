## 2026-11-01 - Swallowed Authorization Exception
**Vulnerability:** HTTPException raised for revoked JWTs was caught and suppressed by a generic `except Exception:` block, causing revocation checks to be bypassed.
**Learning:** Broad exception handling in authentication/authorization logic can inadvertently bypass critical security flows by swallowing expected exceptions like HTTP 401s.
**Prevention:** Explicitly catch and re-raise expected HTTPExceptions before using broad exception blocks, or avoid broad `except Exception:` in security-critical paths altogether.
