import asyncio
import logging
from typing import Callable, Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')

async def with_retry(
    func: Callable[..., Any],
    *args: Any,
    max_attempts: int = 3,
    base_delay_ms: int = 100,
    **kwargs: Any
) -> Any:
    """
    Executes a function with exponential backoff on failure.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            # Check if func is an async function or synchronous
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Action failed after {max_attempts} attempts: {e}", exc_info=True)
                raise e

            delay = (base_delay_ms * (2 ** (attempt - 1))) / 1000.0
            logger.warning(f"Action failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s...")
            await asyncio.sleep(delay)
