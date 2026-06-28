import re

with open("backend/app/core/subscribers.py", "r") as f:
    content = f.read()

# is_active == True ?
# wait, maybe it's just not committing the associations in the test correctly because of concurrent session.
