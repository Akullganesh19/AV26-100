import asyncio
import logging
import inspect
import time
import redis.asyncio as redis
from functools import wraps
from typing import Callable, Any, TypeVar, Optional, Dict

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection pool for idempotency checking
redis_client = redis.from_url(str(settings.CELERY_BROKER_URL), decode_responses=True)

class CircuitBreakerOpenException(Exception):
    pass

def with_retry(max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Retries an async function with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Retry mechanism exhausted for {func.__name__} after {max_attempts} attempts: {e}")
                        raise

                    logger.warning(
                        f"RECOVERY FIRED: Retry {attempt}/{max_attempts} for {func.__name__} due to {type(e).__name__}: {e}. "
                        f"Waiting {delay}s before next attempt."
                    )

                    # Fallback/failure mode for the recovery mechanism itself:
                    # if sleep fails (e.g. cancelled), we still propagate the cancellation
                    try:
                        await asyncio.sleep(delay)
                    except asyncio.CancelledError:
                        logger.error(f"Retry mechanism interrupted for {func.__name__}")
                        raise

                    delay = min(delay * 2, max_delay)
        return wrapper
    return decorator

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.monotonic()
        if self.failures >= self.failure_threshold and self.state != "OPEN":
            self.state = "OPEN"
            logger.critical(f"RECOVERY FIRED: Circuit breaker OPENED after {self.failures} failures.")

    def record_success(self):
        if self.state == "HALF-OPEN" or self.failures > 0:
            logger.info("RECOVERY FIRED: Circuit breaker CLOSED after successful execution.")
        self.failures = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            current_time = time.monotonic()
            if current_time - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("RECOVERY FIRED: Circuit breaker HALF-OPEN, testing availability.")
                return True
            return False
        if self.state == "HALF-OPEN":
            # In half-open, we allow one execution.
            # If it fails, it records failure and opens immediately.
            # If it succeeds, it closes.
            # But wait, we might have multiple concurrent requests in half-open state.
            # To be safe, we let them try, if one fails it goes back to OPEN.
            return True
        return True

def with_circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 30.0, fallback_func: Optional[Callable] = None):
    """
    Circuit breaker pattern to fail fast when a service is degraded.
    """
    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(failure_threshold, recovery_timeout)

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not breaker.can_execute():
                logger.warning(f"Circuit breaker is OPEN for {func.__name__}. Call rejected.")
                if fallback_func:
                    logger.info(f"Executing fallback for {func.__name__} due to OPEN circuit breaker.")
                    if asyncio.iscoroutinefunction(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    return fallback_func(*args, **kwargs)
                raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                # We do not record failure if the exception is CircuitBreakerOpenException
                # but since it's inside the try block, it must be from func
                breaker.record_failure()
                if fallback_func:
                    logger.warning(f"Execution failed for {func.__name__}, executing fallback. Error: {e}")
                    if asyncio.iscoroutinefunction(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    return fallback_func(*args, **kwargs)
                raise

        # Attach the breaker instance for testing/introspection
        wrapper.breaker = breaker
        return wrapper
    return decorator

def with_idempotency_guard():
    """
    Ensures that a function is not retried for the same idempotency key if it already succeeded.
    Requires an 'idempotency_key' in kwargs.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # We must inspect to correctly bind arguments in case idempotency_key is positional
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            key = bound_args.arguments.get('idempotency_key')

            if not key:
                logger.warning(f"No idempotency_key provided for {func.__name__}. Proceeding without guard.")
                return await func(*args, **kwargs)

            full_key = f"{func.__name__}:{key}"
            try:
                if await redis_client.get(full_key):
                    logger.info(f"RECOVERY FIRED: Idempotency guard blocked duplicate execution for {full_key}.")
                    # Return None or skip safely depending on idempotency design,
                    # returning None is safest for functions like email or sync.
                    return None
            except Exception as e:
                logger.error(f"Failed to check idempotency key {full_key}: {e}")

            result = await func(*args, **kwargs)

            # Ensure the guard itself has a failure mode - if redis/store fails
            try:
                await redis_client.setex(full_key, 86400, "1")
            except Exception as e:
                logger.error(f"Failed to save idempotency key {full_key}: {e}")
            return result
        return wrapper
    return decorator
