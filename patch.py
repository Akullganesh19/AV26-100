with open("backend/tests/conftest.py", "r") as f:
    content = f.read()

content = content.replace(
    'TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"',
    'TEST_DATABASE_URL = str(settings.DATABASE_URL) if str(settings.DATABASE_URL).endswith("_test") else str(settings.DATABASE_URL) + "_test"'
)

with open("backend/tests/conftest.py", "w") as f:
    f.write(content)
