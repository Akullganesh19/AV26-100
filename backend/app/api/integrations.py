import asyncio
import httpx
from datetime import date
from typing import Optional, List, Dict, Any
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from app.core.utils import with_retry

class WeatherClient:
    """Client for fetching weather data from external API (e.g., Open-Meteo)."""

    def __init__(self):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        # Using a default timeout to prevent hanging forever
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    async def get_daily_weather(
        self, latitude: float, longitude: float, start_date: date, end_date: date
    ) -> Optional[Dict[str, Any]]:
        """Fetches daily weather data with retries."""

        async def _fetch():
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "daily": "temperature_2m_max,precipitation_sum,relative_humidity_2m_mean",
                        "timezone": "auto"
                    }
                )
                response.raise_for_status()
                return response.json()

        try:
            # We add retries for transient API failures
            return await with_retry(_fetch, max_attempts=3, base_delay=1.0)
        except Exception as e:
            # We don't want a single API failure to break the whole ingestion pipeline
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Weather API failed for lat={latitude}, lon={longitude}: {e}")
            return None

    def parse_weather_response(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parses the raw API response into our standard format."""
        if not raw_data or "daily" not in raw_data:
            return []

        daily = raw_data["daily"]
        dates = daily.get("time", [])
        temps = daily.get("temperature_2m_max", [])
        rains = daily.get("precipitation_sum", [])
        humidities = daily.get("relative_humidity_2m_mean", [])

        records = []
        for i in range(len(dates)):
            try:
                records.append({
                    "date": date.fromisoformat(dates[i]),
                    "temperature_c": float(temps[i]) if temps[i] is not None else 0.0,
                    "rainfall_mm": float(rains[i]) if rains[i] is not None else 0.0,
                    "humidity_pct": float(humidities[i]) if humidities[i] is not None else 0.0,
                })
            except (ValueError, TypeError, IndexError):
                continue

        return records

weather_client = WeatherClient()


class IntegrationService:
    def __init__(self):
        # Algolia Setup
        # Use getattr or fallback since ALGOLIA_APP_ID might not be in settings
        import os
        app_id = getattr(settings, 'ALGOLIA_APP_ID', os.environ.get('ALGOLIA_APP_ID', 'test'))
        self.search_client = SearchClient.create(app_id, settings.ALGOLIA_API_KEY or 'test')
        self.index = self.search_client.init_index("districts")

        # SendGrid Setup
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY or 'test')

        # GetStream Setup
        stream_key = os.environ.get('STREAM_API_KEY', 'test')
        stream_secret = os.environ.get('STREAM_API_SECRET', 'test')
        self.stream = StreamChat(api_key=stream_key, api_secret=stream_secret)

    async def sync_district_to_algolia(self, district_data: dict):
        """Indexes district for world-class search performance."""
        district_data["objectID"] = str(district_data["id"])
        # Offload sync I/O to a separate thread with retry
        await with_retry(asyncio.to_thread, self.index.save_object, district_data, max_attempts=3)

    async def send_health_alert_email(self, to_email: str, district_name: str, disease: str, risk_score: float):
        """Sends high-priority alerts via SendGrid."""
        from_email = getattr(settings, 'EMAILS_FROM_EMAIL', 'alert@episense.test')
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=f"CRITICAL: Outbreak Risk in {district_name}",
            plain_text_content=f"High risk detected for {disease}. Score: {risk_score}"
        )
        # Offload sync I/O to a separate thread with retry
        await with_retry(asyncio.to_thread, self.sg.send, message, max_attempts=3)

    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        def _upload():
            return cloudinary.uploader.upload(
                file_bytes,
                resource_type="raw",
                public_id=f"reports/district_{district_id}",
                format="pdf"
            )
        upload_result = await with_retry(asyncio.to_thread, _upload, max_attempts=3)
        return upload_result.get("secure_url")

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()
