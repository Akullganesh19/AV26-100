import logging
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)

@event_bus.on("clinical.screening.high_risk")
async def handle_high_risk_screening(district_id: str, disease: str):
    """
    Listens for high-risk clinical screenings and triggers cluster evaluation.
    This decouples the clinical API from the tactical alerting logic.
    """
    logger.info(f"Listener received high_risk screening event for district {district_id} (disease: {disease})")

    # We must create a fresh database session since the event handler runs in a background task
    async with SessionLocal() as db:
        try:
            await AlertService.evaluate_clinical_cluster(db, district_id, disease)
        except Exception as e:
            logger.error(
                f"Failed to handle high_risk screening event for district {district_id}: {str(e)}",
                exc_info=True
            )
