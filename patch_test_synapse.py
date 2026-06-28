import re

with open("backend/tests/test_synapse.py", "r") as f:
    content = f.read()

content = content.replace('TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"', 'TEST_DATABASE_URL = str(settings.DATABASE_URL)')

with open("backend/tests/test_synapse.py", "w") as f:
    f.write(content)
