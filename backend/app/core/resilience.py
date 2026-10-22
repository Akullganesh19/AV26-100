import asyncio
import logging
from typing import Callable, TypeVar, Any, Awaitable
from functools import wraps
import inspect

logger = logging.getLogger(__name__)

T = TypeVar('T')

async def with_retry(
    func: Callable[..., Any],
    *args: Any,
    max_attempts: int = 3,
    base_delay: float = 0.1,
    **kwargs: Any
) -> Any:
    """
    Executes a callable (sync or async) with exponential backoff on failure.
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
                    f"Retry failed for {func.__name__} after {max_attempts} attempts. Error: {e}"
                )
                raise e

            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                f"Attempt {attempt} failed for {func.__name__} with error: {e}. Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)
