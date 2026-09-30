import sys
import os
sys.path.append(os.path.abspath('backend'))
os.environ["DATABASE_URL"] = "postgresql+asyncpg://episense:episense@localhost:5432/episense_test"
os.environ["SECRET_KEY"] = "test"
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
os.environ["ALGOLIA_API_KEY"] = "dummy"
os.environ["STREAM_API_KEY"] = "dummy"
os.environ["STREAM_API_SECRET"] = "dummy"

from app.core.config import settings
db_url_str = str(settings.DATABASE_URL)
TEST_DATABASE_URL = db_url_str if db_url_str.endswith("_test") else f"{db_url_str}_test"
print(TEST_DATABASE_URL)
