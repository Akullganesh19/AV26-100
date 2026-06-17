import logging
import time
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import SessionLocal
from app.models.district import District
from app.models.user import User
from app.api.integrations import integration_service

logger = logging.getLogger(__name__)

async def send_alert_notification(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    logger.info(
        f"Initiating alert dispatch for {alert_id}",
        extra={
            "district_id": district_id,
            "disease": disease,
            "risk_score": risk_score
        }
    )
    
    try:
        district_name = "Jurisdiction Monitor"
        # Create a new session to query the DB in the background
        async with SessionLocal() as db:
            if district_id:
                try:
                    # Retrieve the district with its associated users
                    district_stmt = select(District).options(selectinload(District.users)).where(District.id == UUID(district_id))
                    result = await db.execute(district_stmt)
                    district = result.scalar_one_or_none()
                    if district:
                        district_name = district.name

                        # Find users attached to this district that want email alerts
                        users_to_notify = [user for user in district.users if user.email_alerts]

                        if users_to_notify:
                            logger.info(f"Dispatching alerts to {len(users_to_notify)} users for district {district_name}")
                            for user in users_to_notify:
                                await integration_service.send_health_alert_email(
                                    to_email=user.email,
                                    district_name=district_name,
                                    disease=disease,
                                    risk_score=risk_score
                                )
                        else:
                            logger.info(f"No active email alerts configured for users in district {district_name}")
                except Exception as db_exc:
                    logger.error(f"Failed to query DB for users in district {district_id}: {db_exc}", exc_info=True)
                    # Proceed with general log anyway

        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}", exc_info=True)
        return {"status": "failed", "error": str(exc)}
