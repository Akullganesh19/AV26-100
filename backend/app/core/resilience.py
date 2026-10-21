import asyncio
import logging
import inspect
from typing import Callable, Any, TypeVar

logger = logging.getLogger(__name__)

async def with_retry(func: Callable[..., Any], *args: Any, max_retries: int = 3, base_delay: float = 0.1, **kwargs: Any) -> Any:
    """
    Executes a callable (sync or async) with exponential backoff for transient failures.
    """
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            last_exception = e
            if attempt == max_retries:
                logger.error(f"Action failed after {max_retries} attempts: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
    raise last_exception
