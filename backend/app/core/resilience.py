import asyncio
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

def with_retry(max_retries: int = 3, base_delay: float = 0.5):
    """
    Retry an async function with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts. Final error: {str(e)}")
                        raise e

                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Attempt {attempt}/{max_retries} failed for {func.__name__} with error: {str(e)}. "
                        f"Retrying in {delay} seconds..."
                    )
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

def with_circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 30.0):
    """
    Circuit breaker for async functions.
    If the function fails `failure_threshold` times in a row, the circuit opens.
    When open, all calls immediately fail with CircuitBreakerOpenException for `recovery_timeout` seconds.
    After the timeout, it allows one test call to pass through (half-open).
    """
    def decorator(func: Callable) -> Callable:
        # State variables
        failures = 0
        state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        last_failure_time = 0.0

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            nonlocal failures, state, last_failure_time

            current_time = asyncio.get_event_loop().time()

            if state == "OPEN":
                if current_time - last_failure_time >= recovery_timeout:
                    # Transition to HALF_OPEN
                    logger.info(f"Circuit breaker for {func.__name__} transitioning to HALF_OPEN state.")
                    state = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker for {func.__name__} is currently OPEN.")

            try:
                result = await func(*args, **kwargs)
                # Success
                if state in ["HALF_OPEN", "OPEN"] or failures > 0:
                    logger.info(f"Circuit breaker for {func.__name__} transitioning to CLOSED state. Recovery successful.")
                failures = 0
                state = "CLOSED"
                return result
            except Exception as e:
                # Failure
                failures += 1
                last_failure_time = asyncio.get_event_loop().time()

                if state == "HALF_OPEN" or failures >= failure_threshold:
                    if state != "OPEN":
                        logger.error(f"Circuit breaker for {func.__name__} OPENED after {failures} consecutive failures. Last error: {str(e)}")
                    state = "OPEN"

                raise e

        return wrapper
    return decorator
