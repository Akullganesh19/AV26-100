import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 1.0, **kwargs) -> Any:
    """
    Retries an async or sync (wrapped in asyncio.to_thread) function with exponential backoff.
    """
    attempt = 1
    while True:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt >= max_attempts:
                logger.error(f"Failed after {max_attempts} attempts: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Transient failure (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
            attempt += 1
