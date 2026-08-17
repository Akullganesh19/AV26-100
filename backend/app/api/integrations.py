import asyncio
import logging
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from app.utils.retry import with_retry

logger = logging.getLogger(__name__)

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
        try:
            # Offload sync I/O to a separate thread, wrap with exponential backoff retry
            await with_retry(asyncio.to_thread, self.index.save_object, district_data)
        except Exception as e:
            # Graceful degradation: log but don't crash primary flow
            logger.error(f"Failed to sync district {district_data['id']} to Algolia after retries: {e}")

    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        message = Mail(
            from_email=settings.EMAILS_FROM_EMAIL,
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )
        try:
            # Offload sync I/O to a separate thread
            # No retry here, SendGrid email sending is non-idempotent without specific tracking
            await asyncio.to_thread(self.sg.send, message)
            return True
        except Exception as e:
            logger.error(f"Failed to send health alert email to {to_email}: {e}")
            return False

    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        try:
            # Offload sync I/O to a separate thread, wrap with exponential backoff retry
            upload_result = await with_retry(
                asyncio.to_thread,
                cloudinary.uploader.upload,
                file_bytes,
                resource_type="raw",
                public_id=f"reports/district_{district_id}",
                format="pdf"
            )
            return upload_result.get("secure_url")
        except Exception as e:
            # Graceful degradation: log and return None instead of crashing
            logger.error(f"Failed to upload report for district {district_id} to Cloudinary after retries: {e}")
            return None

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()