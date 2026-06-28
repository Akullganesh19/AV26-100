import asyncio
import logging
import time
import inspect
from functools import wraps
from typing import Callable, Any
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global redis pool
try:
    redis_url = settings.CELERY_BROKER_URL
    if isinstance(redis_url, str):
        redis_pool = redis.from_url(redis_url, decode_responses=True)
    else:
        redis_pool = redis.from_url(str(redis_url), decode_responses=True)
except Exception:
    redis_pool = redis.from_url("redis://localhost:6379/0", decode_responses=True)

# Local memory fallback for circuit breaker
local_cb_state = {}

class CircuitBreakerOpenException(Exception):
    pass

def with_circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            key = f"cb:{func.__qualname__}"

            # Fetch state (Redis first, fallback to local)
            state = "CLOSED"
            failures = 0
            last_failure = 0.0

            try:
                state_data = await redis_pool.hgetall(key)
                if state_data:
                    state = state_data.get("state", "CLOSED")
                    failures = int(state_data.get("failures", 0))
                    last_failure = float(state_data.get("last_failure", 0.0))
            except Exception as e:
                logger.warning(f"Redis circuit breaker fetch failed for {key}, falling back to local memory: {type(e).__name__}")
                local_state = local_cb_state.get(key, {})
                state = local_state.get("state", "CLOSED")
                failures = local_state.get("failures", 0)
                last_failure = local_state.get("last_failure", 0.0)

            # Use time.time() for distributed consistency across nodes
            current_time = time.time()

            if state == "OPEN":
                if current_time - last_failure > recovery_timeout:
                    state = "HALF_OPEN"
                    logger.info(f"Circuit breaker for {key} entering HALF_OPEN state")
                    try:
                        await redis_pool.hset(key, "state", "HALF_OPEN")
                    except Exception:
                        local_cb_state.setdefault(key, {})["state"] = "HALF_OPEN"
                else:
                    logger.error(f"Circuit breaker for {key} is OPEN. Call rejected.")
                    raise CircuitBreakerOpenException(f"Circuit breaker {key} is OPEN")

            try:
                result = await func(*args, **kwargs)

                # Success - reset
                if state == "HALF_OPEN" or failures > 0:
                    logger.info(f"Circuit breaker for {key} healed, returning to CLOSED state")
                    try:
                        await redis_pool.delete(key)
                    except Exception:
                        local_cb_state[key] = {"state": "CLOSED", "failures": 0, "last_failure": 0.0}

                return result

            except CircuitBreakerOpenException:
                raise
            except Exception as exc:
                # Failure
                new_state = state
                if state == "HALF_OPEN":
                    new_state = "OPEN"
                    logger.error(f"Circuit breaker for {key} tripped back to OPEN on retry")
                else:
                    failures += 1
                    if failures >= failure_threshold:
                        new_state = "OPEN"
                        logger.error(f"Circuit breaker for {key} tripped OPEN after {failures} failures")

                try:
                    await redis_pool.hset(key, mapping={
                        "state": new_state,
                        "failures": failures,
                        "last_failure": current_time
                    })
                except Exception as redis_exc:
                    logger.warning(f"Redis cb update failed: {type(redis_exc).__name__}")
                    local_cb_state[key] = {
                        "state": new_state,
                        "failures": failures,
                        "last_failure": current_time
                    }
                raise exc
        return wrapper
    return decorator

def with_retry(max_retries: int = 3, base_delay: float = 0.1, max_delay: float = 2.0, idempotent: bool = True):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:

            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            kwargs_all = bound_args.arguments

            idem_key = None
            if not idempotent:
                idem_key = kwargs_all.get("idempotency_key")
                if not idem_key:
                    logger.warning(f"Non-idempotent function {func.__qualname__} called without idempotency_key. Proceeding without retries.")
                    return await func(*args, **kwargs)

                guard_key = f"idem:{func.__qualname__}:{idem_key}"
                try:
                    # Use setnx to prevent race conditions atomically
                    acquired = await redis_pool.setnx(guard_key, "1")
                    if not acquired:
                        logger.warning(f"Idempotency guard caught duplicate execution for {guard_key}")
                        return None
                    # Set expiry so we don't leak memory indefinitely
                    await redis_pool.expire(guard_key, 86400)
                except Exception as e:
                    logger.warning(f"Redis idempotency check failed: {type(e).__name__}. Proceeding cautiously without retry.")
                    # In a true failure we can't guarantee idempotency. Proceed without retry.
                    return await func(*args, **kwargs)

            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except CircuitBreakerOpenException as cbo:
                    # Do not retry if circuit breaker is already open
                    raise cbo
                except Exception as exc:
                    if attempt == max_retries:
                        logger.error(f"Exhausted {max_retries} retries for {func.__qualname__}. Final failure: {type(exc).__name__}")
                        # if we exhaust retries on an idempotency key, we may optionally clear it so a user can retry later.
                        # However, depending on the error, the external call might have succeeded partially. Better safe than double-send.
                        raise exc

                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(f"Retry {attempt}/{max_retries} for {func.__qualname__} in {delay}s due to: {type(exc).__name__}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
