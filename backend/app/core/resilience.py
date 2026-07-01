import asyncio
import functools
import logging
import time
from typing import Callable, Any

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

# We will maintain an in-memory state for circuit breakers
# as `redis.asyncio` should ideally use a connection pool,
# but using an in-memory dict keyed by `func.__qualname__` prevents state collisions.
circuit_breaker_states = {}

def with_retry(max_attempts: int = 3, initial_backoff_ms: int = 100):
    """
    Retry logic with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}")
                        raise e
                    backoff = initial_backoff_ms * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}. Retrying in {backoff} ms... Error: {str(e)}")
                    await asyncio.sleep(backoff / 1000.0)
        return wrapper
    return decorator

def with_circuit_breaker(failure_threshold: int = 3, recovery_timeout_sec: int = 30):
    """
    Circuit breaker pattern to prevent cascading failures.
    Tracks state per function in memory.
    """
    def decorator(func: Callable) -> Callable:
        key = func.__qualname__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if key not in circuit_breaker_states:
                circuit_breaker_states[key] = {
                    "failures": 0,
                    "state": "CLOSED",  # "CLOSED" (normal), "OPEN" (failing), "HALF_OPEN" (testing recovery)
                    "last_failure_time": 0.0
                }

            state_info = circuit_breaker_states[key]
            current_time = time.monotonic()

            if state_info["state"] == "OPEN":
                if current_time - state_info["last_failure_time"] >= recovery_timeout_sec:
                    logger.info(f"Circuit Breaker for {func.__name__} moving to HALF_OPEN state.")
                    state_info["state"] = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                if state_info["state"] == "HALF_OPEN":
                    logger.info(f"Circuit Breaker for {func.__name__} recovered. Moving to CLOSED state.")
                state_info["failures"] = 0
                state_info["state"] = "CLOSED"
                return result
            except Exception as e:
                # If we're testing recovery and it failed, immediately open again
                if state_info["state"] == "HALF_OPEN":
                    state_info["state"] = "OPEN"
                    state_info["last_failure_time"] = time.monotonic()
                else:
                    state_info["failures"] += 1
                    if state_info["failures"] >= failure_threshold:
                        state_info["state"] = "OPEN"
                        state_info["last_failure_time"] = time.monotonic()
                        logger.error(f"Circuit Breaker for {func.__name__} TRIPPED! Moved to OPEN state.")
                raise e
        return wrapper
    return decorator
