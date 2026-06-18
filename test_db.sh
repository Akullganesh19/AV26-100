export DATABASE_URL="postgresql+asyncpg://episense:episense@localhost/episense"
export SECRET_KEY="test_secret_key"
cd backend && alembic upgrade head
