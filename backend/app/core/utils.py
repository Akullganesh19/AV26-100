import asyncio
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=1.0, **kwargs):
    """
    Executes an async function with exponential backoff retry.
    """
    func_name = getattr(func, '__name__', str(func))
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Function {func_name} failed after {max_attempts} attempts. Error: {e}")
                raise e
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                f"Function {func_name} failed (attempt {attempt}/{max_attempts}). "
                f"Retrying in {delay} seconds. Error: {e}"
            )
            await asyncio.sleep(delay)
