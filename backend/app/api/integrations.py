import asyncio
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings


import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=0.1, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Action failed after {max_attempts} attempts: {e}")
                raise e
            logger.warning(f"Attempt {attempt} failed, retrying in {base_delay}s... Error: {e}")
            await asyncio.sleep(base_delay)
            base_delay *= 2

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
        async def _sync():
            return await asyncio.to_thread(self.index.save_object, district_data)

        try:
            await with_retry(_sync)
        except Exception as e:
            logger.error(f"Algolia sync failed ultimately: {e}")
            return None

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
            await asyncio.to_thread(self.sg.send, message)
        except Exception as e:
            logger.error(f"SendGrid email failed to send: {e}")
            return None

    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        async def _upload():
            return await asyncio.to_thread(
                cloudinary.uploader.upload,
                file_bytes,
                resource_type="raw",
                public_id=f"reports/district_{district_id}",
                format="pdf"
            )

        try:
            upload_result = await with_retry(_upload)
            return upload_result.get("secure_url")
        except Exception as e:
            logger.error(f"Cloudinary upload failed ultimately: {e}")
            return None

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()