import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import SessionLocal
from app.services.ingestion_service import ingestion_service
from app.ml.train import train_model

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scheduled_weather_ingestion():
    logger.info("Running scheduled weather ingestion...")
    async with SessionLocal() as db:
        await ingestion_service.run_weather_ingestion(db)

async def scheduled_model_retraining():
    logger.info("Running scheduled model retraining...")
    try:
        await train_model()
    except Exception as e:
        logger.error(f"Scheduled training failed: {e}")

def start_scheduler():
    # 1. Daily Weather Ingestion at 01:00 AM
    scheduler.add_job(
        scheduled_weather_ingestion,
        CronTrigger(hour=1, minute=0),
        id="weather_sync",
        replace_existing=True
    )
    
    # 2. Weekly Model Retraining every Sunday at 03:00 AM
    scheduler.add_job(
        scheduled_model_retraining,
        CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="model_retrain",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("APScheduler: Started background jobs.")

def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler: Shutdown background jobs.")
