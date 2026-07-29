import asyncio
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, **kwargs):
    """
    Executes an async function with exponential backoff retries.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Action failed after {max_attempts} attempts: {e}")
                raise e

            backoff = 0.1 * (2 ** (attempt - 1))
            logger.warning(f"Action failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {backoff}s...")
            await asyncio.sleep(backoff)
