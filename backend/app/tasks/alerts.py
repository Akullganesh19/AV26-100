import logging

logger = logging.getLogger(__name__)


async def send_alert_notification(
    alert_id: str,
    district_name: str,
    disease: str,
    risk_score: float,
    user_email: str = None,
    user_name: str = None,
):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    extra_context = {
        "district": district_name,
        "disease": disease,
        "risk_score": risk_score,
    }
    if user_email:
        extra_context["user_email"] = user_email

    logger.info(f"Initiating alert dispatch for {alert_id}", extra=extra_context)

    try:
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        if user_email:
            logger.info(
                f"DISPATCH TO {user_email} ({user_name}): Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}"
            )
        else:
            logger.info(
                f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}"
            )

        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ...

        return {"status": "dispatched", "alert_id": alert_id}

    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
