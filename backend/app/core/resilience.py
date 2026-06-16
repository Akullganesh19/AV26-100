import asyncio
import functools
import logging
import time
import json
from enum import Enum
from typing import Callable, Any, TypeVar, Optional
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Basic in-memory circuit breaker states per function name
class CircuitState(Enum):
    CLOSED = "CLOSED"     # Normal operation
    OPEN = "OPEN"         # Failing, stop trying
    HALF_OPEN = "HALF_OPEN" # Testing if recovered

class CircuitBreakerConfig:
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0.0

breaker_states: dict[str, CircuitBreakerConfig] = {}


def with_retry(
    max_retries: int = 3,
    base_delay: float = 0.1,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for exponential backoff retry.
    Retries the wrapped async function upon catching specified exceptions.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            while attempt <= max_retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(
                            f"Retry exhausted for {func.__name__} after {max_retries} attempts. Final error: {str(e)}"
                        )
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Attempt {attempt}/{max_retries} failed for {func.__name__}. Retrying in {delay}s. Error: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator


def with_circuit_breaker(
    failure_threshold: int = 3,
    recovery_timeout: float = 30.0,
):
    """
    Decorator for Circuit Breaker pattern.
    If failure_threshold is reached, trips to OPEN and fast-fails requests.
    After recovery_timeout, transitions to HALF_OPEN to test recovery.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            name = f"{func.__module__}.{func.__qualname__}"
            if name not in breaker_states:
                breaker_states[name] = CircuitBreakerConfig()

            cb = breaker_states[name]

            if cb.state == CircuitState.OPEN:
                if time.time() - cb.last_failure_time > recovery_timeout:
                    logger.info(f"Circuit Breaker [{name}] transitioning to HALF_OPEN to test recovery.")
                    cb.state = CircuitState.HALF_OPEN
                else:
                    raise RuntimeError(f"Circuit Breaker [{name}] is OPEN. Fast-failing.")

            try:
                result = await func(*args, **kwargs)
                if cb.state == CircuitState.HALF_OPEN:
                    logger.info(f"Circuit Breaker [{name}] recovered. Transitioning to CLOSED.")
                    cb.state = CircuitState.CLOSED
                    cb.failures = 0
                return result
            except Exception as e:
                cb.failures += 1
                cb.last_failure_time = time.time()
                if cb.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN] and cb.failures >= failure_threshold:
                    logger.critical(f"Circuit Breaker [{name}] tripped to OPEN after {cb.failures} failures.")
                    cb.state = CircuitState.OPEN
                raise
        return wrapper
    return decorator


def with_dead_letter_queue(queue_name: str = "dead-letter"):
    """
    Decorator that catches any unhandled exception in an async background task
    and pushes the task context (arguments, error) to a Redis dead-letter queue.
    Prevents silent background job failures.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Task {func.__name__} failed fatally. Sending to DLQ '{queue_name}'. Error: {str(e)}")

                # Best-effort push to DLQ
                r = None
                try:
                    r = redis.from_url(str(settings.CELERY_BROKER_URL))

                    # Try to serialize args/kwargs, fallback to str if not JSON serializable
                    def safe_serialize(obj):
                        try:
                            json.dumps(obj)
                            return obj
                        except (TypeError, ValueError):
                            return str(obj)

                    safe_args = [safe_serialize(a) for a in args]
                    safe_kwargs = {k: safe_serialize(v) for k, v in kwargs.items()}

                    payload = {
                        "task": f"{func.__module__}.{func.__qualname__}",
                        "args": safe_args,
                        "kwargs": safe_kwargs,
                        "error": str(e),
                        "timestamp": time.time()
                    }

                    await r.lpush(queue_name, json.dumps(payload))
                except Exception as dlq_err:
                    logger.critical(f"Failed to push to DLQ '{queue_name}' for task {func.__name__}. Error: {str(dlq_err)}")
                finally:
                    if r is not None:
                        await r.aclose()

                raise # Re-raise original error so monitoring tools see it as failed
        return wrapper
    return decorator
