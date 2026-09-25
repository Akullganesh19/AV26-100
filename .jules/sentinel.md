## 2025-09-25 — Auth Bypass via Fail-Open Token Revocation Check
**Vulnerability class:** AuthZ / Improper Error Handling
**Entry point:** Any authenticated endpoint relying on `get_current_user` in `backend/app/api/deps.py`.
**Fix:** Modified the `get_current_user` dependency. When checking the Redis revocation list, caught exceptions are no longer silently passed. Additionally, if the Redis cache is unreachable, the API now fails closed by throwing a 503 instead of allowing potentially revoked tokens to proceed.
**Blast radius before fix:** An attacker whose token was revoked could bypass the revocation entirely by sending a malformed JWT (causing an exception during `get_unverified_claims` extraction that was swallowed) or by triggering a DoS condition on the Redis cache, falling back to a standard validation that ignored revocation state.
**Next opportunity:** Investigate other fail-open dependencies or exception swallowing related to external authorization checks (e.g., Clerk API).
