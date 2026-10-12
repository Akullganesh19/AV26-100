import asyncio
import logging
import inspect
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar('T')

async def with_retry(func: Callable[..., Any], *args: Any, max_attempts: int = 3, base_delay: float = 0.1, **kwargs: Any) -> T:
    """
    Auto-Retry with Exponential Backoff.
    Builds self-healing against transient failures in external dependencies.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            res = func(*args, **kwargs)
            if inspect.isawaitable(res):
                return await res
            return res
        except Exception as err:
            if attempt == max_attempts:
                logger.error(f"Recovery failed after {max_attempts} attempts for {getattr(func, '__name__', str(func))}: {err}")
                raise err
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Transient failure in {getattr(func, '__name__', str(func))}: {err}. Retrying in {delay}s (Attempt {attempt}/{max_attempts})...")
            await asyncio.sleep(delay)
