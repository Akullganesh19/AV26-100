## 2024-05-24 — Security Flaws in Authentication Dependency

**Attacked:** `backend/app/api/deps.py`
**Found:**
1. `get_current_user` catches all exceptions during token revocation check and silently passes, bypassing intended security revocation if an exception like network error occurs. Wait, actually, the Redis check raises `HTTPException`, but the `except Exception:` catches it and falls through, completely defeating the revocation list!
2. `get_user_id` extracts user IDs from `jwt.get_unverified_claims(token)`. An attacker can forge the `sub` claim to bypass rate limits by assigning their requests to arbitrary user IDs!

**Severity:** 🔴
**Fixed or flagged:** Fixed
**Systemic pattern:** Broad try/catch hiding critical logic failures. Trusting unverified client input for security mechanisms (rate limiting).
