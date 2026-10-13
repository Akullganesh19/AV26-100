## 2024-10-13 — [Background Tasks and API Resilience]
**Failure point found:** Fire-and-forget background tasks (like `send_alert_notification`) were spawned with `asyncio.create_task` but not stored, risking silent destruction by the garbage collector. Additionally, third-party API calls (Algolia, SendGrid, Cloudinary) had no retry logic on transient failure.
**Why it existed:** Native `asyncio.create_task` behavior is often misunderstood to keep tasks alive indefinitely. Third-party IO was likely written as a quick integration without full resilience guarantees.
**Recovery built:** Added `dispatch_background_task` to keep strong references to tasks and log unhandled exceptions. Added exponential backoff `with_retry` wrapper to third-party integrations and task dispatches.
**Blast radius before:** High priority alerts could fail silently without trace or get randomly dropped mid-execution by the GC.
**Watch for:** Other background queue tasks without retries or `asyncio.create_task` uses scattered in route handlers.
