## 2025-05-15 - Redundant Database Name Generation in Testing
**Failure point found:** `conftest.py` appended `_test` blindly to `DATABASE_URL`, causing `episense_test_test` which fails DB initialization in GitHub CI.
**Why it existed:** It assumed `DATABASE_URL` always pointed to the main db (e.g., `episense`). In CI, it often points directly to a pre-provisioned test DB.
**Recovery built:** Added a conditional check `if str(settings.DATABASE_URL).endswith("_test")` to only append the suffix if missing.
**Blast radius before:** Full CI test suite failure due to missing database `InvalidCatalogNameError`.
**Blast radius after:** 0 - handles both local development configs and CI configs safely.
**Logging/alerting:** N/A.
**Remaining failure points:** N/A.
