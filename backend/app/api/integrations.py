import asyncio
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings

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
        await asyncio.to_thread(self.index.save_object, district_data)

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
        upload_result = cloudinary.uploader.upload(
            file_bytes,
            resource_type="raw",
            public_id=f"reports/district_{district_id}",
            format="pdf"
        )
        return upload_result.get("secure_url")

    async def notify_activity_feed(self, user_id: str, message: str):
        """Pushes a notification to the GetStream activity feed."""
        # Logic for real-time notification push
        pass

integration_service = IntegrationService()

import httpx
from datetime import date
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=0.1, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPError as err:
            logger.warning(f"Attempt {attempt} failed: {err}")
            if attempt == max_attempts:
                logger.error(f"All {max_attempts} attempts failed.")
                raise err

            delay = base_delay * (2 ** (attempt - 1))
            logger.info(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

class WeatherClient:
    def __init__(self):
        self.base_url = settings.OPENMETEO_BASE_URL

    async def get_daily_weather(self, latitude: float, longitude: float, start_date: date, end_date: date):
        async def _fetch():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/archive",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "daily": "temperature_2m_max,precipitation_sum,relative_humidity_2m_mean",
                        "timezone": "auto"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        # Use exponential backoff for resilience against transient failures
        return await with_retry(_fetch, max_attempts=3)

    def parse_weather_response(self, data: dict):
        # Parse the data
        if not data or "daily" not in data:
            return []

        daily = data["daily"]
        dates = daily.get("time", [])
        temps = daily.get("temperature_2m_max", [])
        rains = daily.get("precipitation_sum", [])
        hums = daily.get("relative_humidity_2m_mean", [])

        records = []
        for i in range(len(dates)):
            records.append({
                "date": dates[i],
                "temperature_c": temps[i] if temps[i] is not None else 0,
                "rainfall_mm": rains[i] if rains[i] is not None else 0,
                "humidity_pct": hums[i] if hums[i] is not None else 0,
            })
        return records

weather_client = WeatherClient()
