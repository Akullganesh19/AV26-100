# The error in CI was:
# ERROR backend/tests/ml/test_features.py::test_feature_pipeline_sql_lags - asyncpg.exceptions.InvalidCatalogNameError: database "episense_test_test" does not exist

# Wait, look at tests/conftest.py:
# TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"

# In the CI environment, github actions:
# DATABASE_URL: ***localhost:5432/episense_test
# Then it appends "_test" again:
# episense_test_test
