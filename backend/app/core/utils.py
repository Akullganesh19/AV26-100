import asyncio
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, **kwargs):
    """
    Exponential backoff retry mechanism for transient network and external API failures.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                raise e

            sleep_time = 0.1 * (2 ** (attempt - 1))
            logger.warning(f"Function {func.__name__} attempt {attempt} failed, retrying in {sleep_time}s: {e}")
            await asyncio.sleep(sleep_time)
