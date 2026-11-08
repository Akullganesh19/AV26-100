import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, **kwargs) -> Any:
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Final attempt {attempt} failed for {func.__name__}: {e}")
                raise e

            backoff_time = 0.1 * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {backoff_time}s...")
            await asyncio.sleep(backoff_time)
