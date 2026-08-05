import asyncio
import logging
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=0.1, **kwargs):
    """
    Executes a function with exponential backoff retries.
    Returns None instead of crashing if all attempts fail, ensuring graceful degradation.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Ultimate failure in {func.__name__} after {max_attempts} attempts: {e}")
                return None
            logger.warning(f"Attempt {attempt} failed in {func.__name__}: {e}. Retrying...")
            await asyncio.sleep(base_delay * (2 ** (attempt - 1)))


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
        # Offload sync I/O to a separate thread and wrap with retry
        await with_retry(asyncio.to_thread, self.index.save_object, district_data)

    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        message = Mail(
            from_email=settings.EMAILS_FROM_EMAIL,
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )
        # Offload sync I/O to a separate thread
        await asyncio.to_thread(self.sg.send, message)

    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        # Wrap the blocking cloudinary API call in a thread and retry on failure
        upload_result = await with_retry(
            asyncio.to_thread,
            cloudinary.uploader.upload,
            file_bytes,
            resource_type="raw",
            public_id=f"reports/district_{district_id}",
            format="pdf"
        )

        if upload_result is None:
            return None

        return upload_result.get("secure_url")

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()