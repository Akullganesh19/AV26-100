import asyncio
import logging
from typing import TypeVar, Callable, Any, Coroutine

logger = logging.getLogger(__name__)

T = TypeVar('T')

async def with_retry(
    fn: Callable[..., Coroutine[Any, Any, T]],
    *args,
    max_attempts: int = 3,
    base_delay: float = 0.1,
    **kwargs
) -> T:
    """
    Auto-Retry with Exponential Backoff mechanism.
    Attempts the function up to `max_attempts` times.
    """
    fn_name = getattr(fn, "__name__", str(fn))
    for attempt in range(1, max_attempts + 1):
        try:
            return await fn(*args, **kwargs)
        except Exception as err:
            if attempt == max_attempts:
                logger.error(f"Final retry attempt {attempt}/{max_attempts} failed for {fn_name}: {err}")
                raise err
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt}/{max_attempts} failed for {fn_name} with error: {err}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
