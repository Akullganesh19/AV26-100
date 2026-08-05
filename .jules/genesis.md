## 2024-05-18 — Self-Healing Integrations
**Failure point found:** Algolia search indexing and Cloudinary report uploads were making synchronous, non-retried API calls that could block the async event loop and crash the calling service.
**Why it existed:** Quick implementation assumed external services were always available and fast.
**Recovery built:** Implemented `with_retry` function wrapping `asyncio.to_thread` for external API calls, providing exponential backoff up to 3 attempts, and graceful degradation (returning None) on ultimate failure.
**Blast radius before:** Silent system crashes affecting district syncs and report generation.
**Watch for:** Other non-critical auxiliary integrations that lack idempotency guards or retry logic.
