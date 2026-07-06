filepath = 'backend/tests/conftest.py'
with open(filepath, 'r') as f:
    content = f.read()

# Replace TEST_DATABASE_URL logic
new_logic = """
# Use the dedicated test database created in the previous step
db_url = str(settings.DATABASE_URL)
if not db_url.endswith("_test"):
    TEST_DATABASE_URL = db_url + "_test"
else:
    TEST_DATABASE_URL = db_url
"""

content = content.replace("# Use the dedicated test database created in the previous step\nTEST_DATABASE_URL = str(settings.DATABASE_URL) + \"_test\"", new_logic.strip())

with open(filepath, 'w') as f:
    f.write(content)
