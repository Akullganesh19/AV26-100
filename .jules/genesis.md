## 2024-05-18 — Unprotected External API & DB Task Recovery Built
**Failure point found:**
1) External third-party integrations (Algolia, SendGrid) lacked retry logic and would fail on transient network issues.
2) The critical `evaluate_clinical_cluster` background task lacked retries, meaning transient DB connections would silently swallow cluster alerts.
3) Redis token revocation check in authentication incorrectly fell-open even when `HTTPException` was explicitly raised for revoked tokens.
**Why it existed:** Historical implementations prioritized initial delivery over resilience against transient failures. Redis fail-open logic had an overly broad exception catch.
**Recovery built:**
- Added an `async def with_retry` primitive in `backend/app/core/healing.py` for exponential backoff.
- Wrapped integration calls and cluster evaluation logic in `with_retry`.
- Explicitly caught and re-raised `HTTPException` in the Redis revocation check.
**Blast radius before:** Silent failure of indexing/emails, missed clinical cluster alerts for users, and revoked tokens falsely being allowed if an exception occurred.
**Watch for:** Other background tasks or synchronous integrations lacking idempotency and retry guards.
