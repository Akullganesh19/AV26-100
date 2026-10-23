import asyncio
import logging
import inspect
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args: Any, max_attempts: int = 3, **kwargs: Any) -> Any:
    """
    Auto-Retry with Exponential Backoff for resilient execution of fallible operations.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as exc:
            if attempt == max_attempts:
                logger.error(f"Operation failed after {max_attempts} attempts: {exc}")
                raise
            backoff = 0.1 * (2 ** (attempt - 1))
            logger.warning(f"Transient failure on attempt {attempt}/{max_attempts}, retrying in {backoff}s. Error: {exc}")
            await asyncio.sleep(backoff)
