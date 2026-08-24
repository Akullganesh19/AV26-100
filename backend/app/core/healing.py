import asyncio
import logging
from typing import Callable, Any, TypeVar, Awaitable

logger = logging.getLogger(__name__)

T = TypeVar("T")

async def with_retry(
    func: Callable[..., Awaitable[T]],
    *args,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    exceptions: tuple = (Exception,),
    **kwargs
) -> T:
    """
    Automatic recovery mechanism for transient failures.
    Implements exponential backoff with jitter to prevent thundering herd.
    """
    import random

    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            if attempt == max_attempts:
                logger.error(f"Final attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}")
                raise e

            # Exponential backoff: base_delay * 2^(attempt-1)
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            # Add jitter (0-20%)
            jitter = delay * random.uniform(0, 0.2)
            sleep_time = delay + jitter

            logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__} with error: {str(e)}. Retrying in {sleep_time:.2f}s...")
            await asyncio.sleep(sleep_time)
