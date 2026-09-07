import asyncio
import logging
from typing import Callable, Any, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar('T')

async def with_retry(
    func: Callable[..., Any],
    *args: Any,
    max_attempts: int = 3,
    base_delay: float = 0.1,
    **kwargs: Any
) -> T:
    """
    Executes an async function with exponential backoff retry logic.
    """
    attempt = 1
    while True:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt >= max_attempts:
                logger.error(f"Operation failed after {max_attempts} attempts: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed for {func.__name__}, retrying in {delay}s. Error: {e}")
            await asyncio.sleep(delay)
            attempt += 1
