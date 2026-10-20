## 2024-10-20 — Third-Party Integration Fragility
**Failure point found:** External calls to Algolia, SendGrid, and Cloudinary lacked transient error handling and retry mechanisms. Additionally, the Cloudinary upload was synchronously blocking the async event loop.
**Why it existed:** Third-party SDKs were implemented in the most direct way possible during rapid prototyping without considering network unreliability.
**Recovery built:** Implemented a generic `with_retry` resilience utility in `app.core.resilience` providing exponential backoff, and applied it using `asyncio.to_thread` for non-blocking I/O across all integration calls.
**Blast radius before:** A single transient network hiccup would cause silent failure of critical health alert emails, report uploads, or search index updates, directly impacting operators.
**Watch for:** Similar fragility in `weather_client` or any new external HTTP integrations added in the future.
