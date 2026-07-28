import asyncio
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, **kwargs):
    """
    Wraps an async or sync function with an automatic retry mechanism
    using exponential backoff.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as err:
            if attempt == max_attempts:
                logger.error(f"Failed after {max_attempts} attempts: {err}")
                raise err

            backoff_time = 0.1 * (2 ** (attempt - 1))
            logger.warning(
                f"Attempt {attempt} failed, retrying in {backoff_time:.2f}s... Error: {err}"
            )
            await asyncio.sleep(backoff_time)
