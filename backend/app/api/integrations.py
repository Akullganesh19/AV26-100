import asyncio
import logging
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from typing import Callable

logger = logging.getLogger(__name__)

async def with_retry(func: Callable, *args, max_attempts: int = 3, base_delay: float = 0.5, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Operation failed after {max_attempts} attempts: {str(e)}")
                raise e
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Transient failure: {str(e)}. Retrying in {delay}s (Attempt {attempt}/{max_attempts})...")
            await asyncio.sleep(delay)

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    async def call(self, func: Callable, *args, fallback: Callable = None, **kwargs):
        loop = asyncio.get_running_loop()
        current_time = loop.time()

        if self.state == "OPEN":
            if current_time - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("Circuit Breaker HALF-OPEN. Testing recovery...")
            else:
                if fallback:
                    logger.warning("Circuit Breaker OPEN. Executing fallback.")
                    return await fallback(*args, **kwargs)
                raise Exception("Circuit Breaker OPEN. Fast failing.")

        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF-OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit Breaker CLOSED. Recovery successful.")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = loop.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error("Circuit Breaker TRIPPED (OPEN). Threshold reached.")
            if fallback:
                return await fallback(*args, **kwargs)
            raise e


class IntegrationService:
    def __init__(self):
        # Algolia Setup
        self.search_client = SearchClient.create(settings.ALGOLIA_APP_ID, settings.ALGOLIA_API_KEY)
        self.index = self.search_client.init_index("districts")

        # SendGrid Setup
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        # GetStream Setup
        self.stream = StreamChat(api_key=settings.STREAM_API_KEY, api_secret=settings.STREAM_API_SECRET)

        self.email_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)
        self.algolia_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
        self.cloudinary_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)

    async def sync_district_to_algolia(self, district_data: dict):
        """Indexes district for world-class search performance."""
        district_data["objectID"] = str(district_data["id"])

        async def target():
            return await asyncio.to_thread(self.index.save_object, district_data)

        async def fallback(*args, **kwargs):
            logger.warning(f"Algolia sync degraded for {district_data['objectID']}")
            return None

        return await self.algolia_cb.call(
            with_retry, target, max_attempts=3, base_delay=0.2, fallback=fallback
        )

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

        async def fallback(*args, **kwargs):
            logger.error(f"Failed to send email to {to_email}. Sending to DLQ or logging internally.")
            return None

        return await self.email_cb.call(
            with_retry, target, max_attempts=3, base_delay=0.5, fallback=fallback
        )

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

        async def fallback(*args, **kwargs):
            logger.error(f"Cloudinary upload failed for district {district_id}")
            return None

        upload_result = await self.cloudinary_cb.call(
            with_retry, target, max_attempts=3, base_delay=0.5, fallback=fallback
        )
        if upload_result:
            return upload_result.get("secure_url")
        return None

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()