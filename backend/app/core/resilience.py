import asyncio
import functools
import logging
import time
from enum import Enum
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

def with_retry(max_attempts: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as err:
                    if attempt == max_attempts:
                        logger.error(f"Action failed after {max_attempts} attempts: {err}")
                        raise err
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Action failed. Retrying in {delay}s (Attempt {attempt}/{max_attempts}): {err}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0.0

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                logger.error(f"Circuit breaker tripped! State changing to OPEN after {self.failure_count} failures.")
            self.state = CircuitState.OPEN

    def record_success(self):
        if self.state != CircuitState.CLOSED:
            logger.info("Circuit breaker reset to CLOSED.")
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state.")
                return True
            return False
        if self.state == CircuitState.HALF_OPEN:
            return True
        return True

def with_circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 30.0, fallback_func: Optional[Callable] = None):
    breaker = CircuitBreaker(failure_threshold, recovery_timeout)
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not breaker.can_execute():
                logger.error(f"Circuit breaker for {func.__name__} is OPEN. Fast-failing.")
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                raise Exception(f"Circuit breaker for {func.__name__} is OPEN")

            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                raise e
        return wrapper
    return decorator

def with_dead_letter_queue(queue_name: str = "dead-letter"):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Task {func.__name__} failed permanently. Sending to DLQ '{queue_name}': {e}")
                # Implementation of pushing to DLQ in redis
                try:
                    import redis
                    import json
                    from app.core.config import settings
                    r = redis.from_url(str(settings.CELERY_BROKER_URL))
                    dlq_payload = {
                        "func": func.__name__,
                        "args": args,
                        "kwargs": kwargs,
                        "error": str(e),
                        "timestamp": time.time()
                    }
                    r.rpush(queue_name, json.dumps(dlq_payload))
                except Exception as redis_e:
                    logger.critical(f"Failed to push to DLQ: {redis_e}")
                raise e
        return wrapper
    return decorator
