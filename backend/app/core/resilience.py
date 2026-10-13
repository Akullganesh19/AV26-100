import asyncio
import inspect
import logging
from typing import Callable, Any, Set

logger = logging.getLogger(__name__)

# Strong references for background tasks to prevent mid-execution garbage collection
_background_tasks: Set[asyncio.Task] = set()

def dispatch_background_task(coro) -> asyncio.Task:
    """
    Safely dispatches a fire-and-forget background task.
    Prevents silent garbage collection and logs unhandled failures.
    """
    task = asyncio.create_task(coro)
    _background_tasks.add(task)

    def on_complete(t: asyncio.Task):
        _background_tasks.discard(t)
        try:
            t.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Silent background task failure detected: {str(e)}", exc_info=True)

    task.add_done_callback(on_complete)
    return task

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 1.0, **kwargs) -> Any:
    """
    Auto-retry with exponential backoff for transient failures.
    Supports both standard callables and coroutines.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Final retry attempt {attempt} failed for {func.__name__}: {str(e)}")
                raise

            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                f"Recovery firing: Retry attempt {attempt} for {func.__name__} failed with {type(e).__name__}({str(e)}). "
                f"Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)
