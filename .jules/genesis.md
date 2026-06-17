## 2024-06-17 — [Added Self-Healing Architecture via Retries, Circuit Breakers, and DLQ]
**Failure point found:** External service integrations (SendGrid, Algolia, Cloudinary) and asynchronous background tasks (alerts dispatch) had no error recovery or fault tolerance.
**Why it existed:** Initially developed without robust error-handling for transient failures or external service outages.
**Recovery built:** Created `@with_retry`, `@with_circuit_breaker`, and `@with_dead_letter_queue` decorators in `app/core/resilience.py` and injected them into `IntegrationService` methods and `send_alert_notification`.
**Blast radius before:** Any transient API failure or service outage would silently fail alerts or drop critical background operations forever.
**Watch for:** Other outbound API calls or tasks without explicit retries or DLQ mappings.
