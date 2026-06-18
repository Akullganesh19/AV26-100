from .integrations import integration_service, IntegrationService
from .disease_client import disease_client, DiseaseClient

class MockWeatherClient:
    async def get_daily_weather(self, *args, **kwargs):
        return None
    def parse_weather_response(self, *args, **kwargs):
        return []

weather_client = MockWeatherClient()
