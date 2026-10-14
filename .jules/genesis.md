## 2024-05-15 — Resilient External Integrations & Task GC Protection
**Failure point found:** Unprotected third-party API calls in IntegrationService and background asyncio tasks vulnerable to GC.
**Why it existed:** Assumed `asyncio.to_thread` handled failures, blocking calls missed threads, and `asyncio.create_task` was fire-and-forget safe in Python.
**Recovery built:** Built `with_retry` wrapper with exponential backoff and `isawaitable` checking. Wrapped all I/O calls. Protected background tasks with a strong reference `set()`.
**Blast radius before:** Silent failure of critical health alerts (SendGrid), missing district index updates, and frozen event loops.
**Watch for:** Other `asyncio.create_task` invocations without strong references, and DB commits without retry blocks.
