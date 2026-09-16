## 2024-05-25 — Added Resilience to Third-Party Integrations
**Failure point found:** External API integrations (SendGrid, Algolia, Cloudinary) failed silently or without retries.
**Why it existed:** Quick implementation for MVP.
**Recovery built:** CircuitBreaker applied to Algolia. with_retry (max 3 attempts) applied to SendGrid and Cloudinary.
**Blast radius before:** If third-party APIs failed, entire features like email alerts would fail.
**Watch for:** Other background task integrations that rely on external APIs.
