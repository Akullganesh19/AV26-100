import asyncio
import inspect
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 0.1, **kwargs) -> Any:
    """
    Executes a function with exponential backoff retry logic.
    Handles both synchronous and asynchronous functions, including those returning awaitables.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Action failed after {max_attempts} attempts: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Transient failure in {func.__name__}, retrying in {delay}s (Attempt {attempt}/{max_attempts}): {e}")
            await asyncio.sleep(delay)
