from backend.app.core.config import settings

print(f"DATABASE_URL is: {settings.DATABASE_URL}")
print(f"TEST_DATABASE_URL is: {str(settings.DATABASE_URL) + '_test'}")
