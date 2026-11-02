import asyncio
import inspect
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable[..., Any], *args: Any, max_retries: int = 3, base_delay: float = 0.1, **kwargs: Any) -> Any:
    """
    Executes a callable with exponential backoff for transient failures.
    Supports both synchronous and asynchronous functions.
    """
    for attempt in range(1, max_retries + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"Final attempt failed for {getattr(func, '__name__', 'func')}: {str(e)}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed for {getattr(func, '__name__', 'func')}: {str(e)}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
