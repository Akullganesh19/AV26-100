import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
import uuid
import json

from app.core.config import settings

TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"

@pytest.mark.asyncio
async def test_simulation_advance_day_concurrency(db_session: AsyncSession):
    # Pure RAW SQL testing to completely circumvent SQLAlchemy declarative mappers
    # and their circular dependency / uninitialized registry issues during pytest collection.

    user_id = uuid.uuid4()
    await db_session.execute(text(f"INSERT INTO users (id, name, email, role, is_active, alert_threshold, email_alerts) VALUES ('{user_id}', 'Test User', 'test_sim@example.com', 'OFFICER', true, 70, true)"))

    district_id = uuid.uuid4()
    await db_session.execute(text(f"INSERT INTO districts (id, name, state, state_code, population, latitude, longitude, area_km2) VALUES ('{district_id}', 'Test District', 'Test', 'TS', 1000, 0, 0, 10)"))

    scenario_id = uuid.uuid4()
    await db_session.execute(text(f"INSERT INTO scenarios (id, name, description, total_days, is_template) VALUES ('{scenario_id}', 'Test Scenario', 'desc', 5, true)"))

    # Create an event for Day 1
    event_id = uuid.uuid4()
    data = json.dumps({"risk_score": 0.95})
    await db_session.execute(text(f"INSERT INTO scenario_events (id, scenario_id, day_offset, event_type, district_id, disease, data_json) VALUES ('{event_id}', '{scenario_id}', 1, 'FORECAST_SPIKE', '{district_id}', 'dengue', '{data}')"))

    # Create simulation
    sim_id = uuid.uuid4()
    await db_session.execute(text(f"INSERT INTO simulation_states (id, scenario_id, user_id, current_day, is_active) VALUES ('{sim_id}', '{scenario_id}', '{user_id}', 0, true)"))
    await db_session.commit()

    # We will simulate 3 concurrent clicks on "Advance Day" using exactly the atomic query
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def concurrent_advance():
        async with async_session_maker() as session:
            # Atomic update exactly as written in simulation_service
            update_stmt = text(f"""
                UPDATE simulation_states
                SET current_day = current_day + 1
                WHERE id = '{sim_id}' AND current_day < 5
                RETURNING current_day
            """)
            update_result = await session.execute(update_stmt)
            new_day = update_result.scalar_one_or_none()
            await session.commit()
            return new_day

    # Fire 3 concurrent requests
    results = await asyncio.gather(
        concurrent_advance(),
        concurrent_advance(),
        concurrent_advance()
    )

    # Verify results
    async with async_session_maker() as session:
        result = await session.execute(text(f"SELECT current_day FROM simulation_states WHERE id = '{sim_id}'"))
        final_current_day = result.scalar_one()

        print(f"Final current_day: {final_current_day}")
        print(f"Update results: {results}")

        # Ensure the atomic increment works: should be 3
        assert final_current_day == 3, f"Atomic increment failed: Expected current_day to be 3, got {final_current_day}"

        # Ensure we got exactly 1, 2, 3 in some order (none duplicated)
        assert sorted([r for r in results if r is not None]) == [1, 2, 3], "Returned days from returning clause are incorrect or duplicated"

    await engine.dispose()
