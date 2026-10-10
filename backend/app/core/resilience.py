import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay_ms: int = 100, **kwargs) -> Any:
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Recovery failed: {func.__name__} exhausted {max_attempts} attempts. Error: {e}")
                raise
            delay = (base_delay_ms * (2 ** (attempt - 1))) / 1000.0
            logger.warning(
                f"Recovery firing: {func.__name__} failed (attempt {attempt}/{max_attempts}). "
                f"Retrying in {delay}s. Error: {e}"
            )
            await asyncio.sleep(delay)
