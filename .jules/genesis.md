## 2026-10-03 — Add GC Protection and Retry Logic for Alerts

**Failure point found:** Fire-and-forget tasks in prediction service were getting garbage collected. Dispatching alerts lacked retry mechanism against transient failures.
**Why it existed:** Native `asyncio.create_task` doesn't hold strong references to running background tasks. Alerts didn't have exponential backoff.
**Recovery built:** Added `active_tasks` set to protect background tasks and an exponential backoff wrapper `with_retry` for alerts.
**Blast radius before:** Any transient API error on alert dispatch would fail silently. Background tasks would get silently destroyed on GC cycles.
**Watch for:** Other `asyncio.create_task` uses without strong references and any other integrations missing retries.
