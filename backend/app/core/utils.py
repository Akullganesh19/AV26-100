import asyncio
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=0.1, **kwargs):
    """
    Wraps an asynchronous function with retry logic and exponential backoff.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} for {func.__name__} failed: {e}. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
