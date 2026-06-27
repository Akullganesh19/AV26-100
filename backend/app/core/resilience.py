import asyncio
import functools
import logging
import time
from typing import Callable, Any

logger = logging.getLogger(__name__)

def with_retry(max_attempts: int = 3, initial_backoff: float = 0.1):
    """
    Auto-Retry with Exponential Backoff
    Retries the wrapped async function upon failure.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Retry mechanism failed for {func.__name__} after {max_attempts} attempts: {type(e).__name__}")
                        raise
                    backoff = initial_backoff * (2 ** (attempt - 1))
                    logger.warning(f"Retry mechanism fired for {func.__name__}. Attempt {attempt}/{max_attempts} failed: {type(e).__name__}. Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
        return wrapper
    return decorator

class CircuitBreakerState:
    def __init__(self):
        self.state = "closed"
        self.failures = 0
        self.last_failure_time = 0.0

_cb_states = {}

def with_circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0):
    """
    Circuit Breaker
    Fast-fails if the failure threshold is reached, to prevent cascading failures.
    Uses time.monotonic() for state timeouts.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        _cb_states[func.__qualname__] = CircuitBreakerState()

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            state_obj = _cb_states[func.__qualname__]

            if state_obj.state == "open":
                elapsed = time.monotonic() - state_obj.last_failure_time
                if elapsed > recovery_timeout:
                    # Half-open: try once
                    state_obj.state = "half-open"
                    logger.warning(f"Circuit breaker for {func.__name__} entering half-open state.")
                else:
                    logger.error(f"Circuit breaker for {func.__name__} is OPEN. Fast failing.")
                    raise RuntimeError(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                if state_obj.state == "half-open":
                    logger.info(f"Circuit breaker for {func.__name__} recovered and is now CLOSED.")
                    state_obj.state = "closed"
                    state_obj.failures = 0
                return result
            except Exception as e:
                # Don't increment failures for the RuntimeError thrown by this circuit breaker itself
                if isinstance(e, RuntimeError) and "Circuit breaker is OPEN" in str(e):
                    raise
                state_obj.failures += 1
                state_obj.last_failure_time = time.monotonic()
                if state_obj.state == "half-open" or state_obj.failures >= failure_threshold:
                    if state_obj.state != "open":
                        logger.error(f"Circuit breaker fired for {func.__name__}. State is now OPEN.")
                    state_obj.state = "open"
                raise
        return wrapper
    return decorator
