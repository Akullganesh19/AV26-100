import asyncio
import logging
import time
import json
import redis
from functools import wraps
from typing import Any, Callable, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)

def with_retry(max_attempts: int = 3, initial_backoff: float = 0.1):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}")
                        raise
                    sleep_time = initial_backoff * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed, retrying in {sleep_time}s... Error: {str(e)}")
                    await asyncio.sleep(sleep_time)
                    attempt += 1
        return wrapper
    return decorator


class CircuitBreakerOpenException(Exception):
    pass


def with_circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0):
    def decorator(func: Callable) -> Callable:
        state = {
            "failures": 0,
            "last_failure_time": 0.0,
            "state": "CLOSED"
        }

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            now = time.time()
            if state["state"] == "OPEN":
                if now - state["last_failure_time"] > recovery_timeout:
                    state["state"] = "HALF-OPEN"
                    logger.info(f"Circuit breaker for {func.__name__} entering HALF-OPEN state")
                else:
                    logger.error(f"Circuit breaker OPEN for {func.__name__}, fast-failing")
                    raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                if state["state"] in ["HALF-OPEN", "OPEN"]:
                    logger.info(f"Circuit breaker for {func.__name__} reset to CLOSED")
                state["failures"] = 0
                state["state"] = "CLOSED"
                return result
            except Exception as e:
                state["failures"] += 1
                state["last_failure_time"] = time.time()
                if state["failures"] >= failure_threshold:
                    if state["state"] != "OPEN":
                        logger.critical(f"Circuit breaker for {func.__name__} tripped! Entering OPEN state")
                    state["state"] = "OPEN"
                raise
        return wrapper
    return decorator


DEFAULT_DLQ_NAME = "dead-letter"

def push_to_dlq(payload: Dict[str, Any]):
    try:
        r = redis.from_url(str(settings.CELERY_BROKER_URL))
        r.rpush(DEFAULT_DLQ_NAME, json.dumps(payload))
        logger.warning(f"Task pushed to DLQ '{DEFAULT_DLQ_NAME}'")
    except Exception as e:
        logger.error(f"Failed to push to DLQ: {str(e)}")


def with_dead_letter_queue():
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Function {func.__name__} failed, sending to DLQ. Error: {str(e)}")
                payload = {
                    "function": func.__name__,
                    "args": [str(a) for a in args],
                    "kwargs": {k: str(v) for k, v in kwargs.items()},
                    "error": str(e)
                }
                push_to_dlq(payload)
                raise
        return wrapper
    return decorator
