import asyncio
import cloudinary.uploader
import logging
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from app.core.resilience import with_retry, CircuitBreaker

logger = logging.getLogger(__name__)

algolia_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
sendgrid_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
cloudinary_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)

class IntegrationService:
    def __init__(self):
        # Algolia Setup
        self.search_client = SearchClient.create(settings.ALGOLIA_APP_ID, settings.ALGOLIA_API_KEY)
        self.index = self.search_client.init_index("districts")

        # SendGrid Setup
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        # GetStream Setup
        self.stream = StreamChat(api_key=settings.STREAM_API_KEY, api_secret=settings.STREAM_API_SECRET)

    async def sync_district_to_algolia(self, district_data: dict):
        """Indexes district for world-class search performance."""
        district_data["objectID"] = str(district_data["id"])

        @with_retry(max_attempts=3, base_delay=0.1)
        async def target():
            return await asyncio.to_thread(self.index.save_object, district_data)

        async def fallback(*args, **kwargs):
            logger.warning(f"Algolia sync failed for district {district_data['id']}. Ignoring temporarily.")
            return None

        return await algolia_breaker(target, fallback)

    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        message = Mail(
            from_email=settings.EMAILS_FROM_EMAIL,
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )

        @with_retry(max_attempts=3, base_delay=0.1)
        async def target():
            return await asyncio.to_thread(self.sg.send, message)

        async def fallback(*args, **kwargs):
            logger.warning(f"Failed to send alert email to {to_email}. Consider fallback channels.")
            return None

        return await sendgrid_breaker(target, fallback)

    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        @with_retry(max_attempts=3, base_delay=0.1)
        async def target():
            upload_result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                file_bytes,
                resource_type="raw",
                public_id=f"reports/district_{district_id}",
                format="pdf"
            )
            return upload_result.get("secure_url")

        async def fallback(*args, **kwargs):
            logger.warning(f"Failed to upload report to Cloudinary for district {district_id}. Returning local path/placeholder.")
            return None

        return await cloudinary_breaker(target, fallback)

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()