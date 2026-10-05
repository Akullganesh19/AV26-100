## 2026-10-05 — Silent Background Task Drop & Transient Third-Party Outages
**Failure point found:** Third-party integrations (Algolia, SendGrid, Cloudinary) were completely unprotected against transient network failures (500s/timeouts). Background `send_alert_notification` tasks in prediction service used `asyncio.create_task` with no strong reference collection, leading to silent mid-execution destruction by the garbage collector.
**Why it existed:** The async setup prioritized speed over resilience; integrations assumed perfect network conditions; basic async task firing was used without GC awareness.
**Recovery built:** Introduced `backend/app/core/resilience.py` with `@with_retry` (exponential backoff) and `fire_and_forget` (strong reference set). Wrapped all critical integration API calls and background task launches with these mechanisms.
**Blast radius before:** Silent task destruction meant outbreak alerts could randomly disappear. A 500 error on SendGrid or Algolia would break the user flow and require manual re-submission.
**Watch for:** Other background tasks using bare `asyncio.create_task` and external API calls lacking retry mechanisms.
