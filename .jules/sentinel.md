## 2026-11-03 - Fix Swallowed Exception in Auth Dep
**Vulnerability:** Swallowed HTTP 401 exception in token revocation logic allowed bypassed token revocation checks.
**Learning:** Broad exception catching without explicitly handling or re-raising intentional exceptions (like HTTPException) can inadvertently suppress critical security control flows, leading to authorization bypasses.
**Prevention:** Always explicitly catch and re-raise expected HTTP exceptions before any broad Exception block when dealing with security-critical logic.
