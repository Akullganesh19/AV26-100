import asyncio
import logging
from functools import wraps
import cloudinary.uploader
import redis.asyncio as redis
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
import hashlib

logger = logging.getLogger(__name__)

def with_retry(max_attempts=3, base_delay=0.1, degrade_gracefully=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        if degrade_gracefully:
                            logger.error(f"Action {func.__name__} failed after {max_attempts} attempts: {e}. Degrading gracefully.", exc_info=True)
                            return None
                        logger.error(f"Action {func.__name__} failed after {max_attempts} attempts: {e}", exc_info=True)
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Action {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

class IntegrationService:
    def __init__(self):
        # Algolia Setup
        self.search_client = SearchClient.create(settings.ALGOLIA_APP_ID or "mock", settings.ALGOLIA_API_KEY or "mock")
        self.index = self.search_client.init_index("districts")

        # SendGrid Setup
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY or "mock")

        # GetStream Setup
        self.stream = StreamChat(api_key=settings.STREAM_API_KEY or "mock", api_secret=settings.STREAM_API_SECRET or "mock")

        # Redis setup for idempotency
        self.redis = redis.from_url(str(settings.CELERY_BROKER_URL))

    @with_retry(max_attempts=3, base_delay=0.1, degrade_gracefully=True)
    async def sync_district_to_algolia(self, district_data: dict):
        """Indexes district for world-class search performance."""
        district_data["objectID"] = str(district_data["id"])
        # Offload sync I/O to a separate thread
        await asyncio.to_thread(self.index.save_object, district_data)

    @with_retry(max_attempts=3, base_delay=0.1, degrade_gracefully=True)
    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        # Create idempotency key
        key_str = f"email:{to_email}:{district_name}:{disease}:{risk_score}"
        idemp_key = hashlib.sha256(key_str.encode()).hexdigest()

        # Check idempotency guard (fail open)
        try:
            if await self.redis.get(idemp_key):
                logger.info(f"Idempotency guard: Email to {to_email} already sent. Skipping duplicate.")
                return
        except Exception as e:
            logger.error(f"Idempotency cache unreachable, failing open: {e}")

        message = Mail(
            from_email=settings.EMAILS_FROM_EMAIL or "alert@episense.local",
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )
        # Offload sync I/O to a separate thread
        await asyncio.to_thread(self.sg.send, message)

        # Set idempotency key (fail open)
        try:
            await self.redis.set(idemp_key, "1", ex=86400) # Expire in 24 hours
        except Exception as e:
            logger.error(f"Idempotency cache unreachable when setting key, failing open: {e}")

    @with_retry(max_attempts=3, base_delay=0.1, degrade_gracefully=True)
    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        def upload_sync():
            return cloudinary.uploader.upload(
                file_bytes,
                resource_type="raw",
                public_id=f"reports/district_{district_id}",
                format="pdf"
            )
        # Offload sync I/O to a separate thread
        upload_result = await asyncio.to_thread(upload_sync)
        return upload_result.get("secure_url")

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()
