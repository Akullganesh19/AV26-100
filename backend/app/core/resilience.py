import asyncio
import logging
from functools import wraps
from typing import Callable, Any, Type, Tuple

logger = logging.getLogger(__name__)

def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Auto-Retry with Exponential Backoff.
    Retries an asynchronous function upon failure.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            delay = base_delay
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"RECOVERY FAILED: {func.__name__} failed after {max_attempts} attempts. Final error: {e}",
                            exc_info=True
                        )
                        raise
                    logger.warning(
                        f"RECOVERY INITIATED: {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s. Error: {e}"
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
                    delay = min(delay * exponential_base, max_delay)
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        if self.state != "CLOSED":
            logger.info("CIRCUIT RECOVERED: Transitioning to CLOSED state")
        self.failures = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        if self.failures >= self.failure_threshold:
            if self.state != "OPEN":
                logger.error(f"CIRCUIT TRIPPED: Transitioning to OPEN state after {self.failures} failures")
            self.state = "OPEN"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            current_time = asyncio.get_event_loop().time()
            if current_time - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        if self.state == "HALF_OPEN":
            return True  # Allow one test request
        return False

def with_circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0, fallback_func: Callable = None):
    """
    Circuit Breaker pattern.
    Stops calling the wrapped function if it fails consecutively `failure_threshold` times.
    """
    circuit = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not circuit.can_execute():
                logger.warning(f"CIRCUIT OPEN: {func.__name__} execution prevented.")
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                raise CircuitBreakerOpenException(f"Circuit is open for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                circuit.record_success()
                return result
            except Exception as e:
                circuit.record_failure()
                if fallback_func:
                    logger.warning(f"CIRCUIT FALLBACK: {func.__name__} failed, using fallback.")
                    return await fallback_func(*args, **kwargs)
                raise
        return wrapper
    return decorator

def with_dead_letter_queue(queue_name: str = "dead_letter_queue"):
    """
    Dead Letter Queue pattern.
    Logs and delegates failed jobs instead of letting them disappear.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"DEAD LETTER QUEUE: {func.__name__} failed. Sending to DLQ {queue_name}. Error: {e}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator
