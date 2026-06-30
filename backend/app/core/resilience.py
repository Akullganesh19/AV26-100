import asyncio
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

# In-memory circuit breaker state tracker
_circuit_breaker_states = {}

class CircuitState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

def with_retry(max_retries=3, base_delay=0.1, max_delay=5.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__qualname__} failed after {max_retries} retries.")
                        raise e

                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"Attempt {attempt} for {func.__qualname__} failed: {e}. "
                        f"Retrying in {delay} seconds..."
                    )
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

def with_circuit_breaker(failure_threshold=5, recovery_timeout=30, fallback_func=None, exceptions=(Exception,)):
    def decorator(func):
        key = func.__qualname__

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if key not in _circuit_breaker_states:
                _circuit_breaker_states[key] = {
                    "state": CircuitState.CLOSED,
                    "failures": 0,
                    "last_failure_time": 0.0
                }

            state_info = _circuit_breaker_states[key]

            # Check if OPEN
            if state_info["state"] == CircuitState.OPEN:
                elapsed = time.monotonic() - state_info["last_failure_time"]
                if elapsed >= recovery_timeout:
                    # Transition to HALF_OPEN
                    logger.info(f"Circuit breaker for {key} entering HALF_OPEN state.")
                    state_info["state"] = CircuitState.HALF_OPEN
                else:
                    # Circuit is still OPEN, return fallback or raise exception
                    if fallback_func is not None:
                        logger.warning(f"Circuit breaker OPEN for {key}. Using fallback.")
                        if asyncio.iscoroutinefunction(fallback_func):
                            return await fallback_func(*args, **kwargs)
                        return fallback_func(*args, **kwargs)
                    else:
                        raise RuntimeError(f"Circuit breaker OPEN for {key}. Fast failing.")

            # Execution
            try:
                result = await func(*args, **kwargs)

                # If we were in HALF_OPEN and succeeded, reset to CLOSED
                if state_info["state"] == CircuitState.HALF_OPEN:
                    logger.info(f"Circuit breaker for {key} recovered. State is now CLOSED.")
                    state_info["state"] = CircuitState.CLOSED
                    state_info["failures"] = 0

                # If CLOSED and succeeded, reset failures just in case
                elif state_info["state"] == CircuitState.CLOSED:
                    state_info["failures"] = 0

                return result

            except exceptions as e:
                # We encountered a failure
                state_info["failures"] += 1
                state_info["last_failure_time"] = time.monotonic()

                if state_info["state"] == CircuitState.HALF_OPEN:
                    logger.warning(f"Circuit breaker for {key} failed in HALF_OPEN state. Transitioning back to OPEN.")
                    state_info["state"] = CircuitState.OPEN

                elif state_info["failures"] >= failure_threshold:
                    logger.error(f"Circuit breaker for {key} tripped! Too many failures ({state_info['failures']}). Transitioning to OPEN.")
                    state_info["state"] = CircuitState.OPEN

                if fallback_func is not None:
                    if asyncio.iscoroutinefunction(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    return fallback_func(*args, **kwargs)

                raise e

        return wrapper
    return decorator
