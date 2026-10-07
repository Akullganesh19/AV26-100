import re

with open("backend/tests/conftest.py", "r") as f:
    content = f.read()

new_content = content.replace(
    'TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"',
    'db_url = str(settings.DATABASE_URL).rstrip("/")\nTEST_DATABASE_URL = db_url if db_url.endswith("_test") else db_url + "_test"'
)

with open("backend/tests/conftest.py", "w") as f:
    f.write(new_content)
