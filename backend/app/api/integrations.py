import asyncio
import logging
import redis.asyncio as redis
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, **kwargs):
    """
    Wraps an async function with an exponential backoff retry mechanism.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                raise e
            backoff = 0.1 * (2 ** (attempt - 1))
            logger.warning(f"Transient error in {func.__name__} (attempt {attempt}/{max_attempts}): {e}. Retrying in {backoff}s...")
            await asyncio.sleep(backoff)

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
        try:
            district_data["objectID"] = str(district_data["id"])
            # Wrap in with_retry and to_thread
            await with_retry(
                asyncio.to_thread,
                self.index.save_object,
                district_data,
                max_attempts=3
            )
        except Exception as e:
            # Graceful degradation: log error but don't crash the core transaction
            logger.error(f"Algolia indexing failed for district {district_data.get('id')}: {e}")
            return None

    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        idempotency_key = f"alert_email:{to_email}:{district_name}:{disease}:{risk_score}"
        r = None

        # 1. Idempotency Check (Fail Open)
        try:
            r = redis.from_url(str(settings.CELERY_BROKER_URL))
            if await r.get(idempotency_key):
                logger.info(f"Duplicate email alert suppressed for {district_name} ({disease})")
                await r.aclose()
                return
        except Exception as e:
            logger.warning(f"Idempotency cache unreachable, proceeding without suppression: {e}")

        # 2. Dispatch Email (No retry loop for non-idempotent operation without API-level idempotency key)
        try:
            message = Mail(
                from_email=settings.EMAILS_FROM_EMAIL or "noreply@episense.org",
                to_emails=to_email,
                subject=f"CRITICAL: Outbreak Risk in {district_name}",
                plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
            )

            await asyncio.to_thread(self.sg.send, message)

            # 3. Mark as sent (expire after 24h)
            if r:
                try:
                    await r.setex(idempotency_key, 86400, "sent")
                except Exception as e:
                    logger.warning(f"Failed to set idempotency key after send: {e}")

        except Exception as e:
            logger.error(f"Failed to send health alert email to {to_email}: {e}")
        finally:
            if r:
                try:
                    await r.aclose()
                except Exception:
                    pass

    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        try:
            # Wrap the sync Cloudinary call in asyncio.to_thread and with_retry
            upload_result = await with_retry(
                asyncio.to_thread,
                cloudinary.uploader.upload,
                file_bytes,
                resource_type="raw",
                public_id=f"reports/district_{district_id}",
                format="pdf",
                max_attempts=3
            )
            return upload_result.get("secure_url")
        except Exception as e:
            # Graceful degradation: log error and return None instead of crashing
            logger.error(f"Cloudinary upload failed for district {district_id}: {e}")
            return None

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()