import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 1.0, **kwargs) -> Any:
    """
    Auto-Retry with Exponential Backoff for transient failures.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Final attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}")
                raise e
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
