import asyncio
import logging
from functools import wraps
from typing import Callable, Any, Type, Tuple

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    """Raised when the circuit breaker is open and calls are blocked."""
    pass

def with_retry(
    max_retries: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Retry failed for {func.__name__} after {max_retries} attempts: {e}")
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

def with_circuit_breaker(
    failure_threshold: int = 3,
    recovery_timeout: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    def decorator(func: Callable) -> Callable:
        failures = 0
        last_failure_time = 0.0
        state = "CLOSED"

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            nonlocal failures, last_failure_time, state

            current_time = asyncio.get_event_loop().time()

            if state == "OPEN":
                if current_time - last_failure_time > recovery_timeout:
                    state = "HALF_OPEN"
                    logger.info(f"Circuit breaker for {func.__name__} entering HALF_OPEN state")
                else:
                    logger.error(f"Circuit breaker for {func.__name__} is OPEN. Blocking call.")
                    raise CircuitBreakerOpenException(f"Circuit breaker for {func.__name__} is OPEN")

            try:
                result = await func(*args, **kwargs)
                if state == "HALF_OPEN":
                    state = "CLOSED"
                    failures = 0
                    logger.info(f"Circuit breaker for {func.__name__} closed successfully")
                elif state == "CLOSED" and failures > 0:
                    failures = 0
                return result
            except exceptions as e:
                failures += 1
                last_failure_time = asyncio.get_event_loop().time()
                if failures >= failure_threshold and state in ("CLOSED", "HALF_OPEN"):
                    state = "OPEN"
                    logger.critical(f"Circuit breaker for {func.__name__} OPENED due to: {e}")
                raise

        return wrapper
    return decorator
