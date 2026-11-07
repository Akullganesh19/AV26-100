import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert import Alert, AlertStatus, AlertType
from app.models.audit_log import PredictionAuditLog
from app.models.prediction import Prediction
from app.models.user import User
from app.models.district import District
from app.core.config import settings
from app.api.integrations import integration_service

logger = logging.getLogger(__name__)

background_tasks = set()

class AlertService:
    @staticmethod
    async def _notify_affected_users(db: AsyncSession, alert: Alert):
        """
        Cross-system intelligence: Alerts ↔ Users.
        Finds users registered to this district who want emails and meet the threshold.
        """
        try:
            # Query for the district name and eligible users in one go
            query = (
                select(User, District.name)
                .join(User.districts)
                .where(
                    and_(
                        District.id == alert.district_id,
                        User.email_alerts == True,
                        User.is_active == True,
                        User.alert_threshold <= alert.risk_score * 100
                    )
                )
            )
            result = await db.execute(query)

            for user, district_name in result.all():
                task = asyncio.create_task(
                    integration_service.send_health_alert_email(
                        to_email=user.email,
                        district_name=district_name,
                        disease=alert.disease,
                        risk_score=float(alert.risk_score)
                    )
                )
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)
                logger.info(f"SYNAPSE: Notification dispatched to {user.email} for {alert.disease} in {district_name}")

        except Exception as e:
            logger.error("Failed to cross-correlate alert with users", exc_info=True)

    @staticmethod
    async def evaluate_clinical_cluster(db: AsyncSession, district_id: str, disease: str):
        """
        Background task to evaluate regional clinical clusters.
        Wrapped in robust error handling to prevent silent mission-level failures.
        """
        try:
            # Lookback: 24 hours
            threshold_time = datetime.utcnow() - timedelta(hours=24)
            
            query = select(func.count(PredictionAuditLog.id)).where(
                and_(
                    PredictionAuditLog.district_id == district_id,
                    PredictionAuditLog.endpoint.contains(disease),
                    PredictionAuditLog.status == "SUCCESS",
                    PredictionAuditLog.risk_score >= 0.7,
                    PredictionAuditLog.timestamp >= threshold_time
                )
            )
            
            result = await db.execute(query)
            count = result.scalar() or 0
            
            if count >= settings.CLINICAL_CLUSTER_THRESHOLD:
                # Check for existing open alert to avoid spam
                existing_query = select(Alert).where(
                    and_(
                        Alert.district_id == district_id,
                        Alert.disease == disease,
                        Alert.alert_type == AlertType.CLINICAL_CLUSTER,
                        Alert.status == AlertStatus.TRIGGERED
                    )
                )
                existing = await db.execute(existing_query)
                if not existing.scalar():
                    new_alert = Alert(
                        district_id=district_id,
                        disease=disease,
                        risk_score=0.88,
                        alert_type=AlertType.CLINICAL_CLUSTER,
                        status=AlertStatus.TRIGGERED,
                        metadata_json=json.dumps({
                            "cluster_size": count,
                            "lookback_hours": 24,
                            "triggered_at": datetime.utcnow().isoformat()
                        })
                    )
                    db.add(new_alert)
                    await db.commit()
                    logger.info(f"TACTICAL ALERT: Clinical cluster detected in {district_id} ({disease})")

                    # SYNAPSE: Connect the new alert to user notifications
                    await AlertService._notify_affected_users(db, new_alert)
        
        except Exception as e:
            logger.error(
                f"MISSION FAILURE: Failed to evaluate clinical cluster for {district_id}",
                extra={"disease": disease, "error": str(e)},
                exc_info=True
            )

    @staticmethod
    async def evaluate_autonomous_outbreak(db: AsyncSession, prediction: Prediction):
        """
        Triggered when the background epidemiological model finishes a run.
        Condition: Prediction risk score > Threshold.
        """
        if prediction.risk_score * 100 > settings.ALERT_THRESHOLD_DEFAULT:
            new_alert = Alert(
                district_id=prediction.district_id,
                disease=prediction.disease,
                risk_score=prediction.risk_score,
                prediction_id=prediction.id,
                alert_type=AlertType.AUTONOMOUS,
                status=AlertStatus.TRIGGERED
            )
            db.add(new_alert)
            await db.commit()

            # SYNAPSE: Connect the new alert to user notifications
            await AlertService._notify_affected_users(db, new_alert)

    @staticmethod
    async def acknowledge_alert(db: AsyncSession, alert_id: str, user_id: str):
        query = select(Alert).where(Alert.id == alert_id)
        result = await db.execute(query)
        alert = result.scalar_one_or_none()
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.utcnow()
            await db.commit()
            return alert
        return None
