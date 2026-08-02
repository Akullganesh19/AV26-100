with open("backend/tests/conftest.py", "r") as f:
    content = f.read()

old = 'TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"'
new = 'TEST_DATABASE_URL = str(settings.DATABASE_URL)\nif not TEST_DATABASE_URL.endswith("_test"):\n    TEST_DATABASE_URL += "_test"'

content = content.replace(old, new)
with open("backend/tests/conftest.py", "w") as f:
    f.write(content)
