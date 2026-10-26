import asyncio
import logging
import inspect
from functools import wraps

logger = logging.getLogger(__name__)

def with_retry(max_attempts: int = 3, base_delay: float = 0.1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    # Execute the callable
                    result = func(*args, **kwargs)

                    # Check if the result itself is awaitable (e.g. from an async func or asyncio.to_thread)
                    if inspect.isawaitable(result):
                        return await result
                    return result
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Function {func.__name__} failed attempt {attempt}/{max_attempts}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
