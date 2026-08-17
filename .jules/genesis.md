## 2024-05-24 — Resilient External Integrations & Token Revocation Fix
**Failure point found:** External integrations (Algolia, Cloudinary, SendGrid) lacked retry logic and graceful degradation, acting as single points of failure. The token revocation check in `deps.py` failed closed by swallowing `HTTPException`s due to a generic exception handler.
**Why it existed:** Fast initial implementation prioritized happy-path execution without considering network unreliability or precise exception scoping.
**Recovery built:** Added a `with_retry` exponential backoff mechanism for idempotent integrations (Algolia, Cloudinary), wrapped Cloudinary uploads in `asyncio.to_thread` to prevent event loop blocking, and added graceful degradation fallbacks. Fixed `deps.py` to explicitly re-raise `HTTPException`s.
**Blast radius before:** Any transient third-party API failure would crash the primary application request. Revoked tokens were still accepted if the revocation check threw an error.
**Watch for:** Other background tasks or synchronous third-party SDK calls that might be blocking the async loop or lacking retry mechanisms.
