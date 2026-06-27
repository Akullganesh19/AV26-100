import logging
from typing import Dict, Optional, Any
from app.worker import celery_app
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_DLQ_NAME = "dead-letter"
DLQ_THRESHOLD = 10

@celery_app.task
def monitor_dlq_depth() -> Optional[Dict[str, Any]]:
    """
    Periodic task to monitor the depth of the dead-letter queue.
    If tasks (e.g. alerts) are stuck in the DLQ, it logs a CRITICAL event.
    In production, this should trigger a PagerDuty or Slack notification.
    """
    try:
        # Using str(url) because Redis client expects a string from Pydantic DSN objects
        r = redis.from_url(str(settings.CELERY_BROKER_URL))
        # Get the number of items in the 'dead-letter' list/queue
        depth = r.llen(DEFAULT_DLQ_NAME)
        
        if depth > DLQ_THRESHOLD:
            logger.critical(
                f"DLQ BREACH: {depth} tasks found in '{DEFAULT_DLQ_NAME}'. "
                "Outbreak alert dispatch may be failing silently."
            )
        elif depth > 0:
            logger.warning(f"DLQ Activity: {depth} tasks in '{DEFAULT_DLQ_NAME}'.")
        
        return {"dlq_depth": depth}
    except Exception as e:
        logger.error(f"Failed to monitor DLQ: {type(e).__name__}")
        return None
