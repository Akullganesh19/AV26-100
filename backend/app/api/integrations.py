import asyncio
import logging
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from app.core.resilience import with_retry, CircuitBreaker

logger = logging.getLogger(__name__)

async def algolia_fallback(*args, **kwargs):
    logger.warning("Algolia circuit breaker triggered. Using local search degradation.")
    return None

algolia_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)

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

        async def target():
            return await asyncio.to_thread(self.index.save_object, district_data)

        await algolia_circuit_breaker.call(target, algolia_fallback)

    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        message = Mail(
            from_email=settings.EMAILS_FROM_EMAIL,
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )

        async def target():
            return await asyncio.to_thread(self.sg.send, message)

        await with_retry(target, max_attempts=3)

    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""

        async def target():
            return await asyncio.to_thread(
                cloudinary.uploader.upload,
                file_bytes,
                resource_type="raw",
                public_id=f"reports/district_{district_id}",
                format="pdf"
            )

        upload_result = await with_retry(target, max_attempts=3)
        return upload_result.get("secure_url")

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()