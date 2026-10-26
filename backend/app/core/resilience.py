import asyncio
import inspect
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 0.1, **kwargs) -> Any:
    """
    Executes a callable (sync or async) with exponential backoff for transient failures.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
