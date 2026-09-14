## 2026-06-16 — Sentinel Security Findings
**Attacked:** Authentication and Rate Limiting (`backend/app/api/deps.py`)
**Found:** 1) `get_user_id` parsed unverified JWT claims for rate limiting, allowing IP blocking bypass by forging the `sub` claim. 2) `get_current_user` swallowed HTTP exceptions from the Redis token revocation check via a broad `except Exception:` block, allowing explicitly revoked tokens to pass standard validation.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Re-routed rate limiting entirely to IP until proper signature validation, and explicitly caught and re-raised `HTTPException` during revocation checks.
**Systemic pattern:** Broad `except Exception:` blocks swallowing critical flow control exceptions, and trusting untrusted input in middleware before formal verification. Check all middleware and exception handlers.
