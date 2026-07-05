import asyncio
from datetime import timedelta
import redis.asyncio as redis
from typing import Optional, Any
import json
import logging
from decimal import Decimal
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis connection pool for caching
_redis_pool: Optional[redis.Redis] = None

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, np.number):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

def get_redis() -> redis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(
            settings.CELERY_BROKER_URL,
            decode_responses=True,
            max_connections=10
        )
    return _redis_pool

async def get_cache(key: str) -> Optional[Any]:
    try:
        r = get_redis()
        val = await r.get(key)
        if val:
            return json.loads(val)
    except Exception as e:
        logger.warning(f"Cache get failed for {key}: {e}")
    return None

async def set_cache(key: str, value: Any, ttl: int = 3600) -> None:
    try:
        r = get_redis()
        await r.setex(key, ttl, json.dumps(value, cls=CustomJSONEncoder))
    except Exception as e:
        logger.warning(f"Cache set failed for {key}: {e}")
