import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Any, Tuple, Type

logger = logging.getLogger(__name__)

def with_retry(
    max_attempts: int = 3,
    initial_backoff: float = 0.1,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Auto-Retry with Exponential Backoff.
    """
    def decorator(func: Callable) -> Callable:
        if not asyncio.iscoroutinefunction(func):
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                attempt = 1
                while True:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt >= max_attempts:
                            logger.error(f"Retry exhausted after {max_attempts} attempts for {func.__name__}: {str(e)}")
                            raise e
                        backoff = initial_backoff * (2 ** (attempt - 1))
                        logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__} ({str(e)}). Retrying in {backoff}s...")
                        time.sleep(backoff)
                        attempt += 1
            return sync_wrapper

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Retry exhausted after {max_attempts} attempts for {func.__name__}: {str(e)}")
                        raise e
                    backoff = initial_backoff * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__} ({str(e)}). Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                    attempt += 1
        return async_wrapper
    return decorator


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def __call__(self, func: Callable) -> Callable:
        if not asyncio.iscoroutinefunction(func):
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                now = time.time()
                if self.state == "OPEN":
                    if now - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                        logger.info(f"Circuit breaker for {func.__name__} entering HALF_OPEN state.")
                    else:
                        logger.error(f"Circuit breaker for {func.__name__} is OPEN. Rejecting request.")
                        raise CircuitBreakerOpenException(f"Circuit breaker OPEN for {func.__name__}")

                try:
                    result = func(*args, **kwargs)
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failure_count = 0
                        logger.info(f"Circuit breaker for {func.__name__} CLOSED after successful recovery.")
                    return result
                except Exception as e:
                    if isinstance(e, CircuitBreakerOpenException):
                        raise e

                    self.failure_count += 1
                    self.last_failure_time = time.time()

                    if self.failure_count >= self.failure_threshold:
                        if self.state != "OPEN":
                            logger.error(f"Circuit breaker for {func.__name__} TRIPPED (OPEN) after {self.failure_count} failures.")
                        self.state = "OPEN"
                    else:
                        if self.state == "HALF_OPEN":
                            self.state = "OPEN"
                            logger.error(f"Circuit breaker for {func.__name__} TRIPPED (OPEN) after failure in HALF_OPEN state.")

                    raise e
            return sync_wrapper

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()
            if self.state == "OPEN":
                if now - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    logger.info(f"Circuit breaker for {func.__name__} entering HALF_OPEN state.")
                else:
                    logger.error(f"Circuit breaker for {func.__name__} is OPEN. Rejecting request.")
                    raise CircuitBreakerOpenException(f"Circuit breaker OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    logger.info(f"Circuit breaker for {func.__name__} CLOSED after successful recovery.")
                return result
            except Exception as e:
                if isinstance(e, CircuitBreakerOpenException):
                    raise e

                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.failure_threshold:
                    if self.state != "OPEN":
                        logger.error(f"Circuit breaker for {func.__name__} TRIPPED (OPEN) after {self.failure_count} failures.")
                    self.state = "OPEN"
                else:
                    if self.state == "HALF_OPEN":
                        self.state = "OPEN"
                        logger.error(f"Circuit breaker for {func.__name__} TRIPPED (OPEN) after failure in HALF_OPEN state.")

                raise e
        return async_wrapper

def with_circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 30.0):
    return CircuitBreaker(failure_threshold, recovery_timeout)
