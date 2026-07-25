import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args: Any, max_attempts: int = 3, base_delay: float = 0.5, **kwargs: Any) -> Any:
    """
    Retries an asynchronous (or wrapped synchronous) function with exponential backoff.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Function {func.__name__} attempt {attempt} failed: {str(e)}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
