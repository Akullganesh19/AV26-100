import asyncio
from typing import Set

# Keep strong references to background tasks to prevent garbage collection mid-execution
_background_tasks: Set[asyncio.Task] = set()

def fire_and_forget(coro):
    """
    Safely executes a coroutine in the background.
    Maintains a strong reference to prevent GC dropping the task.
    """
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
