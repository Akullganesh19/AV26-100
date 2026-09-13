## 2026-06-16 — Swallowed HTTPException bypasses Token Revocation
**Attacked:** `get_current_user` in `backend/app/api/deps.py`
**Found:** The `except Exception:` block meant to fall through if Redis is unavailable inadvertently swallows the `HTTPException` intentionally raised when a token is explicitly flagged as revoked. This allows revoked tokens to continue accessing authenticated routes.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added an explicit `except HTTPException:` block to re-raise intended errors before the broad exception handler. Added a regression test to verify.
**Systemic pattern:** Broad `except Exception:` handlers wrapping custom business logic that raises HTTP exceptions, especially in FastAPI dependencies. Look for other fail-open mechanisms that might swallow security-related exceptions.
