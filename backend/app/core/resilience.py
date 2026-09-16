import asyncio
import logging
import time
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, **kwargs):
    """
    Executes an async function with exponential backoff.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Operation failed after {max_attempts} attempts: {e}")
                raise
            delay = 0.1 * (2 ** (attempt - 1))
            logger.warning(f"Operation failed, retrying in {delay}s (Attempt {attempt}): {e}")
            await asyncio.sleep(delay)

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0.0

    async def call(self, target_func: Callable, fallback_func: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state. Testing dependency...")
            else:
                logger.warning("Circuit breaker OPEN. Executing fallback.")
                return await fallback_func(*args, **kwargs)

        try:
            result = await target_func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit breaker reset to CLOSED. Dependency recovered.")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit breaker TRIPPED (OPEN) after {self.failure_count} failures. Error: {e}")
            else:
                logger.warning(f"Dependency failure {self.failure_count}/{self.failure_threshold}. Error: {e}")

            return await fallback_func(*args, **kwargs)
