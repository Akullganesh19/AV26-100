# 🧹 Warden: Fix TEST_DATABASE_URL in conftest.py

## Phase 1: Orient
Task: Analyze the CI Failure caused by the test database setup and fix it.
Failure: `asyncpg.exceptions.InvalidCatalogNameError: database "episense_test_test" does not exist`

## Phase 2: Hunt
Identified in `backend/tests/conftest.py` that `TEST_DATABASE_URL` was unconditionally appending `_test` to the `DATABASE_URL`. Since CI sets `DATABASE_URL` to `.../episense_test`, this resulted in `episense_test_test`.

## Phase 3: Invent
Plan: Modify `conftest.py` to intelligently append `_test` only if the base `DATABASE_URL` doesn't already end in `_test`.

## Phase 4: Build
Updated `backend/tests/conftest.py`:
```python
db_url = str(settings.DATABASE_URL)
TEST_DATABASE_URL = db_url if db_url.endswith("_test") else db_url + "_test"
```

## Phase 5: Verify
Executed tests locally using `.../episense` and `.../episense_test`. Both passed correctly, validating the fix for local and CI environments.

## Phase 6: PR
Ready to submit PR to fix the test database connection string issue.
