from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn

settings = Settings(DATABASE_URL="postgresql+asyncpg://episense:episense@localhost:5432/episense_test")
db_url_str = str(settings.DATABASE_URL)
print(repr(db_url_str))
print(db_url_str.endswith("_test"))
