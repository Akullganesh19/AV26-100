import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert import Alert, AlertStatus, AlertType
from app.models.audit_log import PredictionAuditLog
from app.models.prediction import Prediction
from app.core.config import settings
from app.core.events import event_bus

logger = logging.getLogger(__name__)

class AlertService:
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

                    event_bus.emit(
                        'alert.triggered',
                        alert_id=str(new_alert.id),
                        district_id=str(district_id),
                        disease=disease,
                        risk_score=float(new_alert.risk_score)
                    )
        
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

            event_bus.emit(
                'alert.triggered',
                alert_id=str(new_alert.id),
                district_id=str(prediction.district_id),
                disease=prediction.disease,
                risk_score=float(prediction.risk_score)
            )

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
