with open("backend/tests/conftest.py", "r") as f:
    c = f.read()
c = c.replace(
    'TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"',
    'TEST_DATABASE_URL = str(settings.DATABASE_URL) if str(settings.DATABASE_URL).endswith("_test") else str(settings.DATABASE_URL) + "_test"'
)
with open("backend/tests/conftest.py", "w") as f:
    f.write(c)

with open("backend/tests/test_simulation_concurrency.py", "r") as f:
    c = f.read()
c = c.replace(
    'TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"',
    'TEST_DATABASE_URL = str(settings.DATABASE_URL) if str(settings.DATABASE_URL).endswith("_test") else str(settings.DATABASE_URL) + "_test"'
)
with open("backend/tests/test_simulation_concurrency.py", "w") as f:
    f.write(c)
