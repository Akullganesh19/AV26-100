import re

with open("backend/tests/test_synapse.py", "r") as f:
    content = f.read()

content = content.replace("import app.core.subscribersfrom app.core.subscribers import notify_users_of_alert\n", "from app.core.subscribers import notify_users_of_alert\n")

with open("backend/tests/test_synapse.py", "w") as f:
    f.write(content)
