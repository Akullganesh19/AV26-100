import sys

filepath = 'backend/tests/conftest.py'
with open(filepath, 'r') as f:
    content = f.read()

search_block = """# Use the dedicated test database created in the previous step
TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test\""""

replace_block = """# Use the dedicated test database created in the previous step
TEST_DATABASE_URL = str(settings.DATABASE_URL)"""

if search_block in content:
    content = content.replace(search_block, replace_block)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Patched conftest.py")
else:
    print("Could not find block in conftest.py")
