import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 0.5, **kwargs) -> Any:
    """
    Auto-Retry with Exponential Backoff.
    Protects against transient network failures and 500s from third-party APIs.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Action failed permanently after {max_attempts} attempts. Error: {str(e)}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Transient failure (attempt {attempt}/{max_attempts}). Retrying in {delay}s... Error: {str(e)}")
            await asyncio.sleep(delay)
