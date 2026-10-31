## 2026-10-31 - [Swallowed Security Exception]
**Vulnerability:** Broad except Exception block was catching and swallowing HTTPException raised for revoked JWTs, allowing authorization bypass.
**Learning:** In FastAPI, HTTPException inherits from Exception. Broad exception catches without explicitly re-raising HTTP exceptions can lead to critical authorization bypasses.
**Prevention:** Always add an explicit except HTTPException: raise before generic except Exception blocks in auth/security dependencies.
