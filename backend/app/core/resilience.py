import asyncio
import logging
from functools import wraps
from typing import Callable, Any, Dict

logger = logging.getLogger(__name__)

class CircuitBreakerError(Exception):
    pass

class IdempotencyError(Exception):
    pass

def with_retry(max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 5.0, exceptions=(Exception,), idempotent_required: bool = False):
    """
    Automatic retries with exponential backoff for transient failures.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):


            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Resilience Failure: Function {func.__name__} failed after {max_attempts} attempts. Error: {str(e)}",
                            exc_info=True
                        )
                        raise



                    logger.warning(f"Resilience Recovery Fired: Function {func.__name__} attempt {attempt} failed: {str(e)}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
        return wrapper
    return decorator


def with_circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0, exceptions=(Exception,)):
    """
    Circuit breaker to fail fast and prevent cascading failures when a dependency is continuously down.
    """
    def decorator(func: Callable):
        state = {
            "failures": 0,
            "state": "CLOSED", # CLOSED, OPEN, HALF_OPEN
            "next_attempt": 0.0
        }

        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = asyncio.get_event_loop().time()

            if state["state"] == "OPEN":
                if current_time >= state["next_attempt"]:
                    logger.info(f"Resilience Circuit Breaker: Function {func.__name__} transitioning from OPEN to HALF_OPEN")
                    state["state"] = "HALF_OPEN"
                else:
                    logger.error(f"Resilience Circuit Breaker: Function {func.__name__} is OPEN. Failing fast.")
                    raise CircuitBreakerError(f"Circuit is OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                if state["state"] == "HALF_OPEN":
                    logger.info(f"Resilience Circuit Breaker: Function {func.__name__} transitioning from HALF_OPEN to CLOSED")
                    state["state"] = "CLOSED"
                    state["failures"] = 0
                return result
            except exceptions as e:
                state["failures"] += 1
                if state["state"] == "HALF_OPEN" or state["failures"] >= failure_threshold:
                    if state["state"] != "OPEN":
                        logger.error(f"Resilience Circuit Breaker: Function {func.__name__} threshold reached ({state['failures']}). Transitioning to OPEN for {recovery_timeout}s. Error: {str(e)}")
                    state["state"] = "OPEN"
                    state["next_attempt"] = current_time + recovery_timeout
                raise
        return wrapper
    return decorator
