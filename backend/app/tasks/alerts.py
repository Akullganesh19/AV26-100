import logging
import time
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.user_district import user_district_association
from app.models.district import District

logger = logging.getLogger(__name__)

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float, user_email: str = None):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    target = f"user {user_email}" if user_email else "general broadcast"
    logger.info(
        f"Initiating alert dispatch for {alert_id} to {target}",
        extra={
            "district": district_name,
            "disease": disease,
            "risk_score": risk_score,
            "user_email": user_email
        }
    )
    
    try:
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT to {target}: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id, "user_email": user_email}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id} to {target}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}

async def dispatch_targeted_alerts(db: AsyncSession, alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Synapse Connection: Correlates an Alert with Users mapped to that District
    whose personalized alert_threshold allows them to receive it.
    """
    normalized_score = risk_score if risk_score > 1 else risk_score * 100

    # Find the district name
    district_res = await db.execute(select(District).where(District.id == district_id))
    district = district_res.scalar_one_or_none()
    district_name = district.name if district else str(district_id)

    # Query users
    stmt = (
        select(User)
        .join(user_district_association, User.id == user_district_association.c.user_id)
        .where(user_district_association.c.district_id == district_id)
        .where(User.is_active == True)
        .where(User.email_alerts == True)
        .where(User.alert_threshold <= normalized_score)
    )

    result = await db.execute(stmt)
    users = result.scalars().all()

    if not users:
        logger.info(f"No targeted users found for alert {alert_id} in {district_name} (thresholds not met or unassigned).")
        return []

    logger.info(f"Cross-System Correlation: Found {len(users)} users matching district {district_name} and threshold <= {normalized_score}")

    import asyncio
    dispatch_results = []

    # Store references to fire-and-forget tasks
    if not hasattr(dispatch_targeted_alerts, "_background_tasks"):
        dispatch_targeted_alerts._background_tasks = set()

    for user in users:
        # Pass the specific target's identifier (email) to the notification task
        task = asyncio.create_task(
            send_alert_notification(
                alert_id=alert_id,
                district_name=district_name,
                disease=disease,
                risk_score=risk_score,
                user_email=user.email
            )
        )
        dispatch_targeted_alerts._background_tasks.add(task)
        task.add_done_callback(dispatch_targeted_alerts._background_tasks.discard)
        dispatch_results.append(task)

    return dispatch_results
