import asyncio
import inspect
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=0.5, operation_name="operation", **kwargs):
    """
    Executes a callable with exponential backoff retry logic.
    Handles both sync and async callables (including asyncio.to_thread).
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"FAILURE: {operation_name} failed after {max_attempts} attempts. Error: {str(e)}")
                raise e

            sleep_time = base_delay * (2 ** (attempt - 1))
            logger.warning(f"RECOVERY FIRED: {operation_name} attempt {attempt} failed ({str(e)}). Retrying in {sleep_time}s...")
            await asyncio.sleep(sleep_time)
