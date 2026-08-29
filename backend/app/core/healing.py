import asyncio
import logging
from typing import TypeVar, Callable, Any, Awaitable
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar("T")

def with_retry(max_attempts: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Final error: {str(e)}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Transient failure in {func.__name__} (attempt {attempt}/{max_attempts}). "
                        f"Retrying in {delay}s. Error: {str(e)}"
                    )
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
