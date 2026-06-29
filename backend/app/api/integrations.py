import asyncio
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from app.core.resilience import with_retry, with_circuit_breaker

class IntegrationService:
    def __init__(self):
        # Algolia Setup
        self.search_client = SearchClient.create(
            getattr(settings, 'ALGOLIA_APP_ID', 'test_id'),
            getattr(settings, 'ALGOLIA_API_KEY', 'test_key')
        )
        self.index = self.search_client.init_index("districts")

        # SendGrid Setup
        self.sg = SendGridAPIClient(getattr(settings, 'SENDGRID_API_KEY', 'test_key'))

        # GetStream Setup
        self.stream = StreamChat(
            api_key=getattr(settings, 'STREAM_API_KEY', 'test_key'),
            api_secret=getattr(settings, 'STREAM_API_SECRET', 'test_secret')
        )

    @with_circuit_breaker(failure_threshold=3, recovery_timeout=60.0)
    @with_retry(max_attempts=3, base_delay=1.0)
    async def sync_district_to_algolia(self, district_data: dict):
        """Indexes district for world-class search performance."""
        district_data["objectID"] = str(district_data["id"])
        # Offload sync I/O to a separate thread
        await asyncio.to_thread(self.index.save_object, district_data)

    @with_circuit_breaker(failure_threshold=2, recovery_timeout=30.0)
    @with_retry(max_attempts=3, base_delay=0.5)
    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        message = Mail(
            from_email=getattr(settings, 'EMAILS_FROM_EMAIL', 'test@test.com'),
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )
        # Offload sync I/O to a separate thread
        await asyncio.to_thread(self.sg.send, message)

    @with_circuit_breaker(failure_threshold=3, recovery_timeout=60.0)
    @with_retry(max_attempts=3, base_delay=1.0)
    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        def _upload():
            return cloudinary.uploader.upload(
                file_bytes,
                resource_type="raw",
                public_id=f"reports/district_{district_id}",
                format="pdf"
            )
        upload_result = await asyncio.to_thread(_upload)
        return upload_result.get("secure_url")

    @with_circuit_breaker(failure_threshold=5, recovery_timeout=30.0)
    @with_retry(max_attempts=2, base_delay=0.5)
    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()
