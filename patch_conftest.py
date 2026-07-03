import os

file_path = "backend/tests/conftest.py"
with open(file_path, "r") as f:
    content = f.read()

old_block = """TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test\""""
new_block = """db_url_str = str(settings.DATABASE_URL)
TEST_DATABASE_URL = db_url_str if db_url_str.endswith("_test") else db_url_str + "_test\""""

content = content.replace(old_block, new_block)
with open(file_path, "w") as f:
    f.write(content)
print("Patched conftest.py successfully.")
