import sys

filepath = 'backend/app/main.py'
with open(filepath, 'r') as f:
    content = f.read()

search_block = """from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.logging import setup_logging"""

replace_block = """from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.logging import setup_logging
import app.core.subscribers  # Initialize EventBus subscribers"""

if search_block in content:
    content = content.replace(search_block, replace_block)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Patched main.py")
else:
    print("Could not find block in main.py")
