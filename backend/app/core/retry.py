import asyncio
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, **kwargs):
    """
    Executes an async function with exponential backoff on failure.

    Args:
        func: The async function to execute.
        *args: Positional arguments for the function.
        max_attempts: Maximum number of attempts before raising the exception.
        **kwargs: Keyword arguments for the function.

    Returns:
        The result of the function execution.

    Raises:
        Exception: If all attempts fail.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Ultimate failure after {max_attempts} attempts for {func.__name__}: {str(e)}")
                raise e

            backoff_delay = 0.1 * (2 ** (attempt - 1))
            logger.warning(
                f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                f"Retrying in {backoff_delay} seconds..."
            )
            await asyncio.sleep(backoff_delay)
