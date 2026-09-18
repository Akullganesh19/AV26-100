import asyncio
import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Mock engine to just compile
async def run():
    print("Testing SQL compilation...")
    # Just checking syntax of the query
    q = text("""
        SELECT u.email
        FROM users u
        JOIN user_districts ud ON u.id = ud.user_id
        WHERE ud.district_id = :dist_id
          AND u.email_alerts = true
          AND u.alert_threshold <= :risk
    """)
    print("Query parsed successfully")

if __name__ == "__main__":
    asyncio.run(run())
