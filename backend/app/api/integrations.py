import asyncio
import cloudinary.uploader
# Use fallback imports to work with different algoliasearch versions
try:
    from algoliasearch.search_client import SearchClient
    ALGOLIA_V3 = True
except ImportError:
    try:
        from algoliasearch.search.client import SearchClientSync
        ALGOLIA_V3 = False
    except ImportError:
        pass # Handle mock environment

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from app.core.resilience import with_retry, with_circuit_breaker

class IntegrationService:
    def __init__(self):
        # Algolia Setup
        if settings.ALGOLIA_API_KEY:
            try:
                if ALGOLIA_V3:
                    self.search_client = SearchClient.create(getattr(settings, "ALGOLIA_APP_ID", ""), settings.ALGOLIA_API_KEY)
                    self.index = self.search_client.init_index("districts")
                else:
                    self.search_client = SearchClientSync(getattr(settings, "ALGOLIA_APP_ID", ""), settings.ALGOLIA_API_KEY)
                    self.index = self.search_client # simplified for v4 mock
            except Exception:
                self.index = None
        else:
            self.index = None

        # SendGrid Setup
        if settings.SENDGRID_API_KEY:
            self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        else:
            self.sg = None

        # GetStream Setup
        # self.stream = StreamChat(api_key=settings.STREAM_API_KEY, api_secret=settings.STREAM_API_SECRET)

    @with_retry(max_retries=3, idempotent=True)
    @with_circuit_breaker(failure_threshold=5, recovery_timeout=60.0)
    async def sync_district_to_algolia(self, district_data: dict):
        """Indexes district for world-class search performance."""
        if not self.index:
            return
        district_data["objectID"] = str(district_data["id"])
        # Offload sync I/O to a separate thread
        if hasattr(self.index, "save_object"):
            await asyncio.to_thread(self.index.save_object, district_data)
        elif hasattr(self.index, "save_objects"):
            await asyncio.to_thread(self.index.save_objects, "districts", [district_data])

    @with_retry(max_retries=3, idempotent=False)
    @with_circuit_breaker(failure_threshold=5, recovery_timeout=60.0)
    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float, idempotency_key: str = None):
        """Sends high-priority alerts via SendGrid."""
        if not self.sg:
            return
        message = Mail(
            from_email="noreply@episense.org",
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )
        # Offload sync I/O to a separate thread
        await asyncio.to_thread(self.sg.send, message)

    @with_retry(max_retries=3, idempotent=True)
    @with_circuit_breaker(failure_threshold=5, recovery_timeout=60.0)
    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        upload_result = cloudinary.uploader.upload(
            file_bytes,
            resource_type="raw",
            public_id=f"reports/district_{district_id}",
            format="pdf"
        )
        return upload_result.get("secure_url")

    @with_retry(max_retries=3, idempotent=True)
    @with_circuit_breaker(failure_threshold=5, recovery_timeout=60.0)
    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()
