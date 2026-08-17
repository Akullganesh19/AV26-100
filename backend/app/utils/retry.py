import asyncio
import logging
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar('T')

async def with_retry(
    func: Callable[..., Any],
    *args,
    max_attempts: int = 3,
    base_delay: float = 0.1,
    **kwargs
) -> Any:
    """
    Executes an async function with exponential backoff.
    Suitable for idempotent operations.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Ultimate failure after {max_attempts} attempts: {e}", exc_info=True)
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
