## 2026-06-22 — [Fail-Open Auth Vulnerability & Signature Mismatch]
**Attacked:** `backend/app/api/deps.py` `get_current_user` dependency
**Found:** Auth failed open on Redis connection error during token revocation check. Additionally, `PyJWTError` exception class mismatch on decoding allowed invalid signatures to bypass, and signature branching was missing between internal and Clerk tokens. Finally, `python-jose` was hallucinated by another agent instead of `PyJWT`.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Changed error handling to re-raise `HTTPException` on revoked tokens, and to raise a 500 error if Redis goes down instead of silencing the exception. Corrected `PyJWT` integration and signature parsing.
**Systemic pattern:** Catching broad `Exception` in security or critical infrastructure flows. Ensure all revocation checks fail closed.
