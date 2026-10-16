import asyncio
import logging
import inspect
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 0.5, **kwargs) -> Any:
    """
    Executes a function with exponential backoff retry.
    Handles both sync functions, async functions, and functions returning awaitables.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Recovery failed: {func.__name__} exhausted {max_attempts} attempts. Error: {str(e)}")
                raise

            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                f"Recovery fired: {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s. Error: {str(e)}"
            )
            await asyncio.sleep(delay)
