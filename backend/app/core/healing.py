import asyncio
import logging
from typing import Callable, Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

async def with_retry(func: Callable[..., Any], *args, max_attempts: int = 3, initial_delay: float = 0.1, **kwargs) -> Any:
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Failed after {max_attempts} attempts: {e}")
                raise e
            delay = initial_delay * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed, retrying in {delay} seconds: {e}")
            await asyncio.sleep(delay)
