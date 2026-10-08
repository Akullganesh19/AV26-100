import asyncio
import logging
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from datetime import date
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

async def with_retry_async(func, *args, max_attempts=3, base_delay=0.1, **kwargs):
    """Executes a function with exponential backoff for transient failures."""
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"Operation failed after {max_attempts} attempts. Error: {str(e)}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Operation failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s. Error: {str(e)}")
            await asyncio.sleep(delay)

class WeatherClient:
    """Resilient client for fetching weather data."""
    async def get_daily_weather(self, latitude: float, longitude: float, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        # Dummy implementation simulating external call
        return [{"date": start_date, "temperature_c": 25.0, "rainfall_mm": 0.0, "humidity_pct": 60.0}]

    def parse_weather_response(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return raw_data

weather_client = WeatherClient()

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
        # Offload sync I/O to a separate thread
        await with_retry_async(asyncio.to_thread, self.index.save_object, district_data)

    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        message = Mail(
            from_email=settings.EMAILS_FROM_EMAIL,
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )
        # Offload sync I/O to a separate thread
        await with_retry_async(asyncio.to_thread, self.sg.send, message)

    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""

        def _upload():
            return cloudinary.uploader.upload(
                file_bytes,
                resource_type="raw",
                public_id=f"reports/district_{district_id}",
                format="pdf"
            )

        upload_result = await with_retry_async(asyncio.to_thread, _upload)
        return upload_result.get("secure_url")

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()