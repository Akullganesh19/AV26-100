## 2024-08-08 — Integrations Self-Healing Recovery

**Failure point found:** External auxiliary integrations (Algolia sync, Cloudinary upload, SendGrid alerts) lacked any retry mechanism or graceful degradation, failing synchronously on transient errors and crashing the primary transaction.
**Why it existed:** It was a quick implementation without robustness, assuming external systems would have 100% uptime.
**Recovery built:** Created a generic `with_retry` decorator for automatic exponential backoff on idempotent calls (Algolia, Cloudinary). Added ultimate failure `try/except` fallbacks returning `None` to prevent auxiliary failures from causing cascading crashes.
**Blast radius before:** Any intermittent failure from Algolia, SendGrid, or Cloudinary would crash the upstream calling service, disrupting core workflows for all users during the outage window.
**Watch for:** Ensure we don't accidentally wrap non-idempotent integrations with retries unless explicit idempotency guards are built (e.g. database locks on IDs).
