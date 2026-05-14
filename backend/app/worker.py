from celery import Celery
from kombu import Exchange, Queue
from app.core.config import settings

celery_app = Celery(
    "episense_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Robust Reliability & DLQ Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Senior Engineering Reliability Gates
    task_acks_late=True,               # Don't acknowledge until task completes
    task_reject_on_worker_lost=True,   # Re-queue if worker crashes mid-task
    worker_prefetch_multiplier=1,      # Process one task at a time for predictability
    
    # Dead-Letter Queue (DLQ) Setup
    task_queues=(
        Queue("default", routing_key="default"),
        Queue("dead-letter", routing_key="dead-letter"),
    ),
    task_default_queue="default",
    task_default_exchange_type="direct",
    task_default_routing_key="default",
    
    # Celery Beat Schedule
    beat_schedule={
        "monitor-dlq-every-30-mins": {
            "task": "app.tasks.monitoring.monitor_dlq_depth",
            "schedule": 1800.0, # 30 minutes
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
