## 2024-05-18 — CI and Test Environment Database URL Fix
**Gap found:** GitHub Actions CI `test` job was failing with `asyncpg.exceptions.InvalidCatalogNameError: database "episense_test_test" does not exist`. Furthermore, `.github/workflows/ci.yml` was using a deprecated Node.js 20 environment on `ubuntu-latest`.
**Why it existed:** `backend/tests/conftest.py` appended `_test` to the `DATABASE_URL` unconditionally. In the CI environment, the `DATABASE_URL` already included `_test`, resulting in it searching for `episense_test_test`.
**Built:** Added a check in `backend/tests/conftest.py` to only append `_test` if `DATABASE_URL` does not already end with it. Updated `.github/workflows/ci.yml` to run on `ubuntu-24.04` to resolve the Node 20 deprecation warning.
**Hot path affected:** CI / CD Pipeline, local test execution.
**Measurable improvement:** CI pipeline passes.
**Next opportunity:** Monitor other GitHub actions for Node 20 deprecation warnings.
