## $(date +%Y-%m-%d) — Fix CI invalid catalog name
**Value type:** N/A
**Drift risk found:** Backend unit tests running in CI failed with `InvalidCatalogNameError: database "episense_test_test" does not exist`.
**Fix:** Removed the `+ "_test"` suffix from `TEST_DATABASE_URL` in `backend/tests/conftest.py`. The CI `DATABASE_URL` environment variable is already correctly configured to use `episense_test`.
**Proven by:** Passing backend tests locally.
**Other balances to check:** None.
