import asyncio
import cloudinary.uploader
try:
    from algoliasearch.search_client import SearchClient
except ImportError:
    from algoliasearch.search.client import SearchClientSync as SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from app.core.resilience import with_retry, with_circuit_breaker

class IntegrationService:
    def __init__(self):
        # Algolia Setup
        algolia_app_id = getattr(settings, 'ALGOLIA_APP_ID', '')
        algolia_api_key = getattr(settings, 'ALGOLIA_API_KEY', '')
        if algolia_app_id and algolia_api_key:
            self.search_client = SearchClient.create(algolia_app_id, algolia_api_key)
            self.index = self.search_client.init_index("districts")
        else:
            self.search_client = None
            self.index = None

        # SendGrid Setup
        sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        if sendgrid_api_key:
            self.sg = SendGridAPIClient(sendgrid_api_key)
        else:
            self.sg = None

        # GetStream Setup
        stream_api_key = getattr(settings, 'STREAM_API_KEY', '')
        stream_api_secret = getattr(settings, 'STREAM_API_SECRET', '')
        if stream_api_key and stream_api_secret:
            self.stream = StreamChat(api_key=stream_api_key, api_secret=stream_api_secret)
        else:
            self.stream = None

    @with_circuit_breaker(failure_threshold=3, recovery_timeout_sec=30)
    @with_retry(max_attempts=3, initial_backoff_ms=100)
    async def sync_district_to_algolia(self, district_data: dict):
        """Indexes district for world-class search performance."""
        if not self.index:
            return
        district_data["objectID"] = str(district_data["id"])
        # Offload sync I/O to a separate thread
        await asyncio.to_thread(self.index.save_object, district_data)

    @with_circuit_breaker(failure_threshold=3, recovery_timeout_sec=30)
    @with_retry(max_attempts=3, initial_backoff_ms=100)
    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        if not self.sg:
            return
        message = Mail(
            from_email=getattr(settings, 'EMAILS_FROM_EMAIL', 'noreply@episense.com'),
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )
        # Offload sync I/O to a separate thread
        await asyncio.to_thread(self.sg.send, message)

    @with_circuit_breaker(failure_threshold=3, recovery_timeout_sec=30)
    @with_retry(max_attempts=3, initial_backoff_ms=100)
    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        upload_result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            file_bytes,
            resource_type="raw",
            public_id=f"reports/district_{district_id}",
            format="pdf"
        )
        return upload_result.get("secure_url")

    @with_circuit_breaker(failure_threshold=3, recovery_timeout_sec=30)
    @with_retry(max_attempts=3, initial_backoff_ms=100)
    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        if not self.stream:
            return
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()
