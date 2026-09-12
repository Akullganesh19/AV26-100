import asyncio
import logging
import time
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, **kwargs) -> Any:
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Failed after {max_attempts} attempts: {e}")
                raise
            backoff = 0.1 * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed, retrying in {backoff}s...")
            await asyncio.sleep(backoff)

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    async def call(self, func: Callable, *args, fallback_func: Callable = None, **kwargs) -> Any:
        now = time.time()
        if self.state == "OPEN":
            if now - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
            else:
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                raise Exception("Circuit Breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF-OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = now
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error("Circuit Breaker transitioned to OPEN")

            if fallback_func:
                return await fallback_func(*args, **kwargs)
            raise
