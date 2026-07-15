import logging
from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.user import User
from app.models.user_district import user_district_association

logger = logging.getLogger(__name__)

async def dispatch_targeted_notifications(district_id: str, disease: str, risk_score: float, source: str):
    """
    Finds and notifies users who are monitoring the specific district,
    have email alerts enabled, and whose thresholds are exceeded.
    """
    try:
        # Convert district_id to string for DB query if it's a UUID
        district_id_str = str(district_id)

        async with SessionLocal() as db:
            # Join users and user_districts to find relevant officers
            query = (
                select(User)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .where(user_district_association.c.district_id == district_id_str)
                .where(User.is_active == True)
                .where(User.email_alerts == True)
            )
            result = await db.execute(query)
            officers = result.scalars().all()

            notified_count = 0
            for officer in officers:
                # Assuming risk_score from predictions/alerts is 0-1, or 0-100.
                # Thresholds are 0-100. If risk_score is <= 1.0, multiply by 100
                normalized_score = risk_score * 100 if risk_score <= 1.0 else risk_score

                if normalized_score >= officer.alert_threshold:
                    # In a real system, send email via external API here
                    logger.info(
                        f"TARGETED NOTIFICATION: Sending alert to {officer.email} for {disease} in {district_id_str} "
                        f"(Score: {normalized_score:.2f} >= Threshold: {officer.alert_threshold})",
                        extra={
                            "user_id": str(officer.id),
                            "district_id": district_id_str,
                            "disease": disease,
                            "risk_score": normalized_score,
                            "threshold": officer.alert_threshold,
                            "source": source
                        }
                    )
                    notified_count += 1

            if notified_count > 0:
                logger.info(f"Targeted notification batch completed. Notified {notified_count} officers.")

    except Exception as e:
        logger.error(f"Failed to dispatch targeted notifications: {e}", exc_info=True)


@event_bus.on("alert.triggered")
async def handle_alert_triggered(payload: dict):
    """
    payload should contain: district_id, disease, risk_score
    """
    await dispatch_targeted_notifications(
        payload.get("district_id"),
        payload.get("disease"),
        payload.get("risk_score", 0.0),
        source="alert"
    )

@event_bus.on("prediction.high_risk")
async def handle_prediction_high_risk(payload: dict):
    """
    payload should contain: district_id, disease, risk_score
    """
    await dispatch_targeted_notifications(
        payload.get("district_id"),
        payload.get("disease"),
        payload.get("risk_score", 0.0),
        source="prediction"
    )
