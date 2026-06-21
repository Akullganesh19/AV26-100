import asyncio
import functools
import logging
from typing import Callable, Any, TypeVar
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar("T")


def with_retry(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0):
    """
    Decorator for exponential backoff retries.
    """

    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            while attempt < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt == max_retries:
                        logger.error(
                            f"RECOVERY FAILED: {func.__name__} exhausted "
                            f"{max_retries} retries. Final error: {str(e)}",
                            exc_info=True,
                        )
                        raise

                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"RECOVERY INITIATED: {func.__name__} failed "
                        f"(attempt {attempt}/{max_retries}). "
                        f"Retrying in {delay}s. Error: {str(e)}"
                    )
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


class CircuitBreakerOpenException(Exception):
    pass


def with_circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0):
    """
    Decorator for circuit breaker pattern.
    """
    # Use a closure to maintain state per-function
    state = {
        "failures": 0,
        "state": "CLOSED",  # CLOSED, OPEN, HALF_OPEN
        "last_failure_time": None,
    }

    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            now = datetime.now()

            if state["state"] == "OPEN":
                delta = (now - state["last_failure_time"]).total_seconds()
                if delta > recovery_timeout:
                    logger.info(
                        f"CIRCUIT BREAKER: Transitioning {func.__name__} "
                        "to HALF_OPEN"
                    )
                    state["state"] = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker for {func.__name__} is OPEN. " "Fast-failing."
                    )

            try:
                result = await func(*args, **kwargs)

                if state["state"] == "HALF_OPEN":
                    logger.info(
                        f"CIRCUIT BREAKER: Transitioning {func.__name__} "
                        "to CLOSED (recovered)"
                    )
                    state["state"] = "CLOSED"
                    state["failures"] = 0

                return result

            except Exception as e:
                state["failures"] += 1
                state["last_failure_time"] = datetime.now()

                cond_open = (
                    state["state"] == "HALF_OPEN"
                    or state["failures"] >= failure_threshold
                )
                if cond_open:
                    if state["state"] != "OPEN":
                        logger.error(
                            f"CIRCUIT BREAKER: Transitioning {func.__name__} "
                            f"to OPEN after {state['failures']} failures."
                        )
                    state["state"] = "OPEN"

                raise e

        return wrapper

    return decorator


def with_dead_letter_queue(queue_name: str):
    """
    Decorator to route failed background task payloads to a Dead Letter Queue.
    """

    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"DLQ ROUTING: Task {func.__name__} failed persistently. "
                    f"Routing to DLQ '{queue_name}'. Error: {str(e)}"
                )
                # Redis/RabbitMQ queue logic here
                raise e

        return wrapper

    return decorator
