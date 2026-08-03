import asyncio
import logging
import inspect
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args: Any, max_attempts: int = 3, base_delay: float = 0.1, **kwargs: Any) -> Any:
    """
    Executes a function with exponential backoff on failure.
    If the function is synchronous, it should be wrapped in `asyncio.to_thread` by the caller
    or handled internally by the caller, but `with_retry` will await if the result is awaitable.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            if attempt == max_attempts:
                logger.error(
                    f"Action failed after {max_attempts} attempts. Final error: {str(e)}",
                    exc_info=True
                )
                raise

            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                f"Action failed on attempt {attempt}/{max_attempts}: {str(e)}. "
                f"Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)
