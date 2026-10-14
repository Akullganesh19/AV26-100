import redis.asyncio as redis
from app.core.config import settings

# Global Redis client to be reused across requests
redis_client = redis.from_url(str(settings.CELERY_BROKER_URL))
