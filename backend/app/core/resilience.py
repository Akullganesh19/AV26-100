import asyncio
import functools
import logging
import time
from typing import Callable, Any, Optional

import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection pool for resilience state
redis_client = redis.from_url(
    str(settings.CELERY_BROKER_URL) if settings.CELERY_BROKER_URL else f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    decode_responses=True
)

class CircuitBreakerOpenException(Exception):
    pass

def with_retry(max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 10.0):
    """
    Auto-Retry with Exponential Backoff
    Retries an async function upon transient failure.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except CircuitBreakerOpenException:
                    # Don't retry if circuit breaker is open
                    raise
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__qualname__} failed after {max_attempts} attempts: {e}")
                        raise

                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"Function {func.__qualname__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {delay} seconds..."
                    )
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    fallback_function: Optional[Callable[..., Any]] = None
):
    """
    Circuit Breaker pattern backed by Redis.
    Uses func.__qualname__ as the state dictionary key equivalent in Redis.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Using func.__qualname__ to prevent collisions
        key_prefix = f"circuit_breaker:{func.__qualname__}"
        failures_key = f"{key_prefix}:failures"
        state_key = f"{key_prefix}:state"
        last_failure_time_key = f"{key_prefix}:last_failure_time"

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                state = await redis_client.get(state_key) or "CLOSED"
            except Exception as e:
                logger.error(f"Failed to check circuit breaker state for {func.__qualname__}: {e}")
                # Degrade gracefully by failing CLOSED: if Redis is down, allow the call anyway
                state = "CLOSED"

            if state == "OPEN":
                try:
                    last_failure_time_str = await redis_client.get(last_failure_time_key)
                except Exception as e:
                    logger.error(f"Failed to check last failure time for {func.__qualname__}: {e}")
                    last_failure_time_str = None

                if last_failure_time_str:
                    last_failure_time = float(last_failure_time_str)
                    # Using epoch time instead of monotonic for distributed compatibility
                    if time.time() - last_failure_time > recovery_timeout:
                        try:
                            await redis_client.set(state_key, "HALF-OPEN")
                            state = "HALF-OPEN"
                            logger.info(f"Circuit breaker for {func.__qualname__} transitioned to HALF-OPEN")
                        except Exception as e:
                            logger.error(f"Failed to update state to HALF-OPEN for {func.__qualname__}: {e}")
                            state = "CLOSED" # Fallback to CLOSED if redis fails
                    else:
                        if fallback_function:
                            return await fallback_function(*args, **kwargs)
                        raise CircuitBreakerOpenException(f"Circuit breaker OPEN for {func.__qualname__}")

            try:
                result = await func(*args, **kwargs)

                if state == "HALF-OPEN":
                    try:
                        await redis_client.set(state_key, "CLOSED")
                        await redis_client.delete(failures_key)
                    except Exception as e:
                        logger.error(f"Failed to update state to CLOSED for {func.__qualname__}: {e}")

                    logger.info(f"Circuit breaker for {func.__qualname__} transitioned to CLOSED")

                return result

            except Exception as e:
                # Do not increment failures for CircuitBreakerOpenException if bubbled from inner decorator
                if isinstance(e, CircuitBreakerOpenException):
                    raise

                try:
                    failures = await redis_client.incr(failures_key)
                    if state == "HALF-OPEN" or failures >= failure_threshold:
                        await redis_client.set(state_key, "OPEN")
                        # Use time.time() for cross-machine consistency
                        await redis_client.set(last_failure_time_key, str(time.time()))
                        logger.error(f"Circuit breaker for {func.__qualname__} transitioned to OPEN. Error: {e}")
                except Exception as redis_e:
                    logger.error(f"Redis error during circuit breaker failure recording for {func.__qualname__}: {redis_e}")
                    # Allow the original exception to bubble up if redis is down

                if fallback_function:
                    return await fallback_function(*args, **kwargs)
                raise

        return wrapper
    return decorator
