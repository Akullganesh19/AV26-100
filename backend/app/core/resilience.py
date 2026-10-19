import asyncio
import inspect
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=0.1, **kwargs):
    """
    Executes a callable (sync or async) with exponential backoff for transient failures.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Operation failed after {max_attempts} attempts: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed, retrying in {delay}s: {e}")
            await asyncio.sleep(delay)
