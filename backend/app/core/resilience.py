import asyncio
import logging
import functools
from typing import Callable, Any

logger = logging.getLogger(__name__)

def with_retry(max_attempts: int = 3, base_delay: float = 0.1, fallback_value: Any = None):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        if fallback_value is not None:
                            logger.info(f"Returning fallback value for {func.__name__}")
                            return fallback_value
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0, fallback_value: Any = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED" # CLOSED, OPEN, HALF-OPEN
        self.fallback_value = fallback_value

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            current_time = asyncio.get_event_loop().time()
            if self.state == "OPEN":
                if current_time - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF-OPEN"
                    logger.info(f"Circuit breaker for {func.__name__} transitioning to HALF-OPEN")
                else:
                    logger.warning(f"Circuit breaker for {func.__name__} is OPEN. Call rejected.")
                    if self.fallback_value is not None:
                         return self.fallback_value
                    raise RuntimeError(f"Circuit breaker open for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    logger.info(f"Circuit breaker for {func.__name__} transitioning to CLOSED")
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = current_time
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.error(f"Circuit breaker for {func.__name__} transitioning to OPEN due to {self.failure_count} failures.")
                if self.fallback_value is not None:
                    return self.fallback_value
                raise

        return wrapper

def with_circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0, fallback_value: Any = None):
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, fallback_value)
    return breaker

def with_dead_letter_queue(queue_func: Callable):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Function {func.__name__} failed, sending to dead letter queue: {e}")
                await queue_func(*args, **kwargs, error=str(e))
                raise
        return wrapper
    return decorator
