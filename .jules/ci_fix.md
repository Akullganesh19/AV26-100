## 2024-05-18 — CI Fix
**Issue:** GitHub Actions CI `test` job failed with `asyncpg.exceptions.InvalidCatalogNameError: database "episense_test_test" does not exist`.
Also there was a warning about Node 20 deprecation.
**Root cause:** `backend/tests/conftest.py` appended `_test` to the `DATABASE_URL` even if it already had it, which caused the CI database to be requested as `episense_test_test` when the CI config had `POSTGRES_DB: episense_test`. Also, `actions/checkout@v4` targets Node 20 by default which is deprecated.
**Fix:** Conditionally append `_test` in `backend/tests/conftest.py` only if `DATABASE_URL` doesn't already end with `_test`. Also added `actions/setup-node@v4` with `node-version: '24'` in `ci.yml`.
