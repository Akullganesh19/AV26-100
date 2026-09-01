import asyncio
import logging

logger = logging.getLogger(__name__)

async def with_retry(fn, max_attempts=3, *args, **kwargs):
    """
    Auto-Retry with Exponential Backoff
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await fn(*args, **kwargs)
        except Exception as err:
            if attempt == max_attempts:
                logger.error(f"Mission failure after {max_attempts} attempts: {err}")
                raise err

            backoff_time = 0.1 * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed, retrying in {backoff_time}s: {err}")
            await asyncio.sleep(backoff_time)
