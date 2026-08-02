import asyncio
from typing import Callable, Any

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 1.0, **kwargs) -> Any:
    pass

print("Syntax valid")
