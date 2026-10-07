1. **Update `backend/tests/conftest.py`**
   - The test CI failed because `TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"` appends `_test` blindly. If the CI supplies `DATABASE_URL` ending with `_test`, it becomes `_test_test`, which causes `asyncpg.exceptions.InvalidCatalogNameError: database "episense_test_test" does not exist`.
   - Following memory: "In pytest `conftest.py` setups for SQLAlchemy, when creating a dedicated test database URL by appending `_test` to the application's `DATABASE_URL`, first strip trailing slashes (e.g., `.rstrip("/")`) before checking if the string already ends with `_test`. This prevents appending the suffix multiple times (e.g., `_test_test`) when CI environments supply database URLs with a trailing slash."
   - I need to fix `conftest.py` to prevent this double suffix issue.

2. **Run tests**
   - No need to run DB tests since I cannot start Postgres locally, but I will compile check.

3. **Complete pre-commit steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

4. **Submit**
   - Submit the PR via `submit` using the branch name `synapse-alert-routing`.
