import asyncio
import cloudinary.uploader
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from stream_chat import StreamChat
from app.core.config import settings
from app.core.utils import with_retry

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
        await with_retry(asyncio.to_thread, self.sg.send, message)

    async def upload_report_to_cloudinary(self, file_bytes: bytes, district_id: str):
        """Uploads generated PDF reports to Cloudinary CDN."""
        upload_result = await with_retry(
            asyncio.to_thread,
            cloudinary.uploader.upload,
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

class WeatherClient:
    """
    Mock client for Open-Meteo or similar weather APIs.
    In production, this would make real HTTP requests.
    """
    async def get_daily_weather(self, latitude: float, longitude: float, start_date, end_date):
        # Replace with real API call in production
        import random
        from datetime import timedelta

        delta = end_date - start_date
        data = {"time": [], "temperature_2m_mean": [], "precipitation_sum": [], "relative_humidity_2m_mean": []}

        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            data["time"].append(day.isoformat())
            data["temperature_2m_mean"].append(random.uniform(20.0, 35.0))
            data["precipitation_sum"].append(random.uniform(0.0, 50.0))
            data["relative_humidity_2m_mean"].append(random.uniform(40.0, 90.0))

        return data

    def parse_weather_response(self, raw_data):
        records = []
        times = raw_data.get("time", [])
        temps = raw_data.get("temperature_2m_mean", [])
        rains = raw_data.get("precipitation_sum", [])
        humids = raw_data.get("relative_humidity_2m_mean", [])

        for i, date_str in enumerate(times):
            records.append({
                "date": date_str,
                "temperature_c": temps[i] if i < len(temps) else None,
                "rainfall_mm": rains[i] if i < len(rains) else None,
                "humidity_pct": humids[i] if i < len(humids) else None,
            })
        return records

weather_client = WeatherClient()
