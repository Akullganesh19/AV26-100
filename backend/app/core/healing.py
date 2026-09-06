import asyncio
import logging
from typing import Callable, Any, TypeVar, Awaitable
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

def with_retry(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    exceptions: tuple = (Exception,)
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Decorator for robust retry logic on async functions with exponential backoff.
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            attempt = 1
            delay = base_delay
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"Max retries ({max_attempts}) reached for {func.__name__}. "
                            f"Final error: {str(e)}",
                            exc_info=True
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {delay} seconds..."
                    )

                    await asyncio.sleep(delay)
                    attempt += 1
                    # Exponential backoff, capped at max_delay
                    delay = min(delay * 2, max_delay)
        return wrapper
    return decorator
