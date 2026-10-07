import asyncio
import logging
from typing import Coroutine, Set, Callable, Any

logger = logging.getLogger(__name__)

_background_tasks: Set[asyncio.Task] = set()

def safe_fire_and_forget(coro: Coroutine, name: str = "background_task") -> asyncio.Task:
    task = asyncio.create_task(coro, name=name)
    _background_tasks.add(task)

    def _on_completion(t: asyncio.Task):
        _background_tasks.discard(t)
        try:
            t.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"🔥 [Genesis] Background task '{t.get_name()}' failed permanently: {e}", exc_info=True)

    task.add_done_callback(_on_completion)
    return task

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 0.1, **kwargs) -> Any:
    for attempt in range(1, max_attempts + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"🔥 [Genesis] Exhausted {max_attempts} retries for {func.__name__}. Final error: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                f"🛡️ [Genesis] Transient failure in {func.__name__}: {e}. "
                f"Auto-recovering... (Attempt {attempt}/{max_attempts}, waiting {delay}s)"
            )
            await asyncio.sleep(delay)
