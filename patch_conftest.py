with open("backend/tests/conftest.py", "r") as f:
    content = f.read()

old_code = 'TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"'
new_code = 'TEST_DATABASE_URL = str(settings.DATABASE_URL)\nif not TEST_DATABASE_URL.endswith("_test"):\n    TEST_DATABASE_URL += "_test"'

content = content.replace(old_code, new_code)

with open("backend/tests/conftest.py", "w") as f:
    f.write(content)
