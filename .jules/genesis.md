## 2025-06-25 — Added integration resilience for external APIs
**Failure point found:** The `IntegrationService` methods that make network calls to external APIs (`Algolia`, `SendGrid`, `Cloudinary`) had no protection. A failure from any of these third-parties or transient network drops would fail the whole request synchronously.
**Why it existed:** The initial implementations were direct wrappers around the external SDKs without any circuit breakers or retries built for the system overall.
**Recovery built:** Created `with_retry` and `with_circuit_breaker` decorators in `backend/app/core/resilience.py`. I also applied them to the external calls inside `IntegrationService`. Additionally, `cloudinary.uploader.upload` blocking I/O was wrapped inside `asyncio.to_thread` for graceful degradation and avoiding blocking the main thread event loop.
**Blast radius before:** Any failure from the third-parties mentioned above would affect the whole API system request for all users using the system.
**Watch for:** Other external SDK calls globally across the codebase that should be wrapped with `asyncio.to_thread` or have resilience configured around them.
