import logging
from app.core.resilience import with_retry

logger = logging.getLogger(__name__)


@with_retry(max_attempts=3, base_delay=2.0)
async def send_alert_notification(
    alert_id: str, district_name: str, disease: str, risk_score: float
):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    logger.info(
        f"Initiating alert dispatch for {alert_id}",
        extra={
            "district": district_name,
            "disease": disease,
            "risk_score": risk_score,
        },
    )

    try:
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(
            f"CRITICAL ALERT: Outbreak risk detected in {district_name} "
            f"({disease}). Score: {risk_score}"
        )

        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ...

        return {"status": "dispatched", "alert_id": alert_id}

    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        raise exc
