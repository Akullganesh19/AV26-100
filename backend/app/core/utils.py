import asyncio
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=0.1, **kwargs):
    """
    Executes an async function with exponential backoff.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Operation failed after {max_attempts} attempts: {e}")
                raise

            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Operation failed, retrying in {delay}s (Attempt {attempt}/{max_attempts}): {e}")
            await asyncio.sleep(delay)
