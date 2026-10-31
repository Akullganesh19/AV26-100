import asyncio
from sqlalchemy import create_engine, text

async def create_test_db():
    # Connect to the default postgres database
    admin_url = "postgresql://episense:episense@localhost:5432/postgres"
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE DATABASE episense_test"))
            print("Database episense_test created.")
        except Exception as e:
            if "already exists" in str(e):
                print("Database episense_test already exists.")
            else:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_db())
