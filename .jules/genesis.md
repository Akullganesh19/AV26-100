## 2024-05-01 — Auto-Retry External Integration I/O and GC Protection
**Failure point found:** External SDK calls lacking retries in `integrations.py`, and `send_alert_notification` unreferenced `asyncio.create_task` vulnerability in `prediction_service.py`.
**Why it existed:** Assumed sunny-day stability of external SDKs (SendGrid, Algolia, Cloudinary) and unawareness of Python garbage collection mechanics destroying unreferenced background tasks. Cloudinary SDK blocking main async event loop.
**Recovery built:** Added `with_retry` exponential backoff mechanism in `app/core/healing.py` applied to external calls via `asyncio.to_thread`. Maintained GC reference tracking via module-level set `background_tasks`.
**Blast radius before:** Transient network blips silently failed synchronization and email alerts. Python GC randomly dropped critical notifications mid-execution. High latency IO requests blocked the entire server.
**Watch for:** Other `asyncio.create_task` usage without `await` and missing `with_retry` on third party integrations.
