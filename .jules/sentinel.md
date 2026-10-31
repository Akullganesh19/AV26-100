## 2026-10-30 - Token Revocation Bypass
**Vulnerability:** HTTP exceptions raised during token revocation checks were swallowed by a broad 'except Exception' block, bypassing the revocation list.
**Learning:** In FastAPI dependencies like get_current_user, avoid using broad except blocks around security-critical logic without first catching and re-raising HTTPException to prevent unintentionally bypassing security controls.
**Prevention:** Always catch and explicitly re-raise HTTPException before generic exception handlers in auth logic.
