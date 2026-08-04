import asyncio
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=0.1, fallback=None, raise_on_failure=True, **kwargs):
    """
    Executes a coroutine function with exponential backoff retries.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            name = getattr(func, "__name__", str(func))
            if attempt == max_attempts:
                logger.error(f"Action {name} failed after {max_attempts} attempts: {e}")
                if raise_on_failure:
                    raise
                return fallback
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Action {name} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
    return fallback
