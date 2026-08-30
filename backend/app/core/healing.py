import asyncio
import logging
from typing import TypeVar, Callable, Any, Awaitable

logger = logging.getLogger(__name__)

T = TypeVar("T")

async def with_retry(func: Callable[..., Awaitable[T]], *args: Any, max_attempts: int = 3, **kwargs: Any) -> T:
    """
    Executes a coroutine with exponential backoff.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Action failed after {max_attempts} attempts: {e}")
                raise
            sleep_ms = 100 * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed, retrying in {sleep_ms}ms: {e}")
            await asyncio.sleep(sleep_ms / 1000.0)
