import asyncio
import functools
import logging
from typing import Coroutine, Set, Callable, TypeVar, Any, cast

logger = logging.getLogger(__name__)

# Strong reference collection for fire-and-forget tasks
_background_tasks: Set[asyncio.Task] = set()

def fire_and_forget(coro: Coroutine, name: str = None) -> asyncio.Task:
    """
    Safely execute a background task.
    Prevents silent destruction by the garbage collector mid-execution.
    """
    task = asyncio.create_task(coro, name=name)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

    def _handle_result(t: asyncio.Task):
        try:
            t.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Unhandled exception in background task {t.get_name() or 'unknown'}: {str(e)}", exc_info=True)

    task.add_done_callback(_handle_result)
    return task

def with_retry(max_attempts: int = 3, base_delay: float = 0.1, exceptions: tuple = (Exception,)):
    """
    Decorator for automatic retry of transient failures with exponential backoff.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Action '{func.__name__}' failed after {max_attempts} attempts. Final error: {str(e)}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Action '{func.__name__}' failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s... Error: {str(e)}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
