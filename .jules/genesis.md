## 2024-08-14 — Integrations Resilience and Fail-Open Auth Fix
**Failure point found:** Third-party integrations (Algolia, SendGrid, Cloudinary) lacked retries and graceful degradation, threatening to crash primary requests. Token revocation failed-open incorrectly by swallowing HTTP 401 exceptions.
**Why it existed:** Happy-path coding and misunderstanding of generic exception handling in fail-open cache patterns.
**Recovery built:** Implemented `with_retry` exponential backoff for Algolia and Cloudinary, added async thread offloading and graceful degradation blocks. Explicitly caught and re-raised `HTTPException` in auth to prevent revoked tokens from succeeding.
**Blast radius before:** High: A single third-party API timeout would crash entire requests (e.g. report generation). Revoked tokens remained valid.
**Watch for:** Other integrations missing `asyncio.to_thread` and fail-open auth blocks swallowing explicit errors.
