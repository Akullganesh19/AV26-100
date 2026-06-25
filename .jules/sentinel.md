## 2025-02-12 — Token Revocation Fail-Open Vulnerability
**Attacked:** `backend/app/api/deps.py` - `get_current_user` token revocation check
**Found:** A generic `except Exception:` block caught all exceptions unconditionally, including the `HTTPException` intentionally raised when a token was revoked, and any `redis.RedisError` when the caching infrastructure failed. This caused the system to fail-open and successfully validate malicious or revoked tokens, allowing unauthorized access.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Added explicit `except HTTPException:` and `except redis.RedisError:` blocks before the broad Exception handler to ensure that infrastructure errors and explicit HTTP errors fail-closed.
**Systemic pattern:** Broad `except Exception:` catching blocks around security, identity, or infrastructure code without re-raising or failing closed.
