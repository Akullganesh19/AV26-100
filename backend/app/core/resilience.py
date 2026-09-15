import asyncio
import logging
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

def with_retry(*, max_attempts: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as err:
                    if attempt == max_attempts:
                        logger.error(f"Action failed after {max_attempts} attempts: {err}")
                        raise err
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} failed, retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

    async def __call__(self, target: Callable, fallback: Callable, *args, **kwargs) -> Any:
        now = asyncio.get_event_loop().time()
        if self.state == "OPEN":
            if now - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                return await fallback(*args, **kwargs)

        try:
            result = await target(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as err:
            self.failure_count += 1
            self.last_failure_time = now
            if self.failure_count >= self.failure_threshold:
                if self.state != "OPEN":
                    logger.error(f"Circuit breaker tripped OPEN after {self.failure_count} failures: {err}")
                self.state = "OPEN"
            return await fallback(*args, **kwargs)
