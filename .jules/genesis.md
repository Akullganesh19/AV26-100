## 2024-05-24 — Unprotected Integration Calls
**Failure point found:** External integrations (Algolia, SendGrid, Cloudinary) lacked transient failure handling.
**Why it existed:** Assumed happy path for 3rd party APIs.
**Recovery built:** Added `with_retry` async utility with exponential backoff for integration methods.
**Blast radius before:** Silent failure in alerts or CDN uploads on transient network drops.
**Watch for:** Other outbound HTTP calls missing resilience wrappers.
