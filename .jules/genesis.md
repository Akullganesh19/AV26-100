## 2024-11-20 — External API Integration Reliability
**Failure point found:** External SDK calls (SendGrid, Algolia, Cloudinary) in `IntegrationService` had no retry logic or circuit breakers. Transient errors would fail operations entirely, and persistent failures could cause cascading latency/hangs or swallow critical alerts in background jobs.
**Why it existed:** Quick initial implementation using synchronous SDKs wrapped in `asyncio.to_thread` without resilience wrappers.
**Recovery built:** Added `with_retry` (exponential backoff) and `CircuitBreaker` classes. Wrapped all 3 external integrations with retries, a circuit breaker, and a fallback logger to degrade gracefully.
**Blast radius before:** Any network hiccup or 3rd-party outage would drop critical emails, break search indexing, or fail report generation.
**Watch for:** Other integrations or background jobs that call out to external HTTP endpoints without resilience wrappers.
