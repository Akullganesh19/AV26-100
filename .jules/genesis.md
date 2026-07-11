## 2025-02-27 — [Missing Retry and Broken Async References]
**Failure point found:** Third-party API calls in `IntegrationService` and `send_alert_notification` background tasks lacked resilience.
**Why it existed:** Initially implemented using naive implementations with `asyncio.to_thread` for external APIs and fire-and-forget `asyncio.create_task` logic without retry configuration or reference holding.
**Recovery built:** Implemented `with_retry` function featuring exponential backoff for `IntegrationService` operations. Additionally, securely anchored `asyncio.create_task` tasks to `_background_tasks` module-level set, utilizing `task.add_done_callback` to enforce complete life-cycle event looping and avoid mid-flight garbage collection.
**Blast radius before:** Any intermittent network hiccups resulted in immediate unrecoverable errors during Algolia, Cloudinary, or SendGrid integration. Tasks dispatched dynamically would be unpredictably destroyed by Python's GC leading to missing critical alerts.
**Watch for:** Other `asyncio.create_task` references without task caching and unhandled third-party dependency issues missing basic exponential retry protection.

## 2025-02-27 — [CI Test Database Misconfiguration]
**Failure point found:** pytest crashed in CI with `asyncpg.exceptions.InvalidCatalogNameError: database "episense_test_test" does not exist`.
**Why it existed:** `backend/tests/conftest.py` unconditionally appended `_test` to `settings.DATABASE_URL`. However, the CI workflow dynamically explicitly configured `DATABASE_URL` as `episense_test`. The naive append logic created an expected connection path for `episense_test_test` which did not exist on the postgres 15 image within GitHub services.
**Recovery built:** Upgraded database connection string appending in `backend/tests/conftest.py` to check for suffix via `_db_url_str.endswith("_test")` safely reverting to `_db_url_str` itself before appending `_test` if missing.
**Blast radius before:** 100% CI failure blocking pipeline merges completely.
**Watch for:** Other naive substring append modifications around URL connection config parsing via Pydantic or environment strings without idempotency.
