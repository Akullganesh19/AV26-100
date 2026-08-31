import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable[..., Any], max_attempts: int = 3, base_delay: float = 0.1) -> Any:
    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Action failed after {max_attempts} attempts: {e}")
                raise e
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Action failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
