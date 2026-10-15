import redis.asyncio as redis
from app.core.config import settings

# Global async Redis client to reuse connection pools across requests
redis_client = redis.from_url(str(settings.CELERY_BROKER_URL))
