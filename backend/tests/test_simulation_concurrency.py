import asyncio
import pytest
import uuid
from sqlalchemy import select
from app.models.scenario import Scenario, ScenarioEvent, SimulationState
from app.models.audit_log import PredictionAuditLog
from app.models.alert import Alert
from app.models.user import User
from app.models.district import District
from app.services.simulation_service import SimulationService

@pytest.mark.asyncio
async def test_concurrent_advance_day(db_session):
    # Setup user, scenario, district
    user = User(name="Test Officer", email="test_sim_concurrency@example.com", password_hash="hash")
    db_session.add(user)

    district = District(name="Test District Sim", state="Test State", state_code="TS", latitude=0, longitude=0, population=1000, area_km2=100)
    db_session.add(district)
    await db_session.commit()

    scenario = Scenario(name="Test Scenario", description="Desc", total_days=5)
    db_session.add(scenario)
    await db_session.commit()

    event = ScenarioEvent(
        scenario_id=scenario.id,
        day_offset=1,
        event_type="CLINICAL_SURGE",
        district_id=district.id,
        disease="cholera",
        data_json={"risk_score": 0.9}
    )
    db_session.add(event)
    await db_session.commit()

    sim = await SimulationService.create_simulation(db_session, str(scenario.id), str(user.id))
    sim_id = str(sim.id)

    # Simulate concurrent advance_day calls
    # We need separate db sessions for true concurrency simulation
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession

    engine = db_session.bind
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def advance_concurrently():
        async with async_session() as session:
            return await SimulationService.advance_day(session, sim_id)

    # Run 2 advances concurrently
    results = await asyncio.gather(
        advance_concurrently(),
        advance_concurrently()
    )

    # Check current_day
    async with async_session() as session:
        result = await session.execute(select(SimulationState).where(SimulationState.id == sim_id))
        final_sim = result.scalar_one()
        # Since they run concurrently and read before writing, both might read current_day=0,
        # increment to 1, and write back 1. Thus current_day would be 1, not 2!
        # The test asserts 2 which means we WANT it to be 2. If it's vulnerable, it will be 1.
        # But actually, let's just observe the duplication for now.

        # Check if events were duplicated
        audit_res = await session.execute(select(PredictionAuditLog).where(PredictionAuditLog.user_id == user.id))
        audits = audit_res.scalars().all()
        # CLINICAL_SURGE inserts 6 logs. Since we only have day 1 event, it should insert 6.
        # If it processed day 1 twice, it would be 12 logs!
        assert len(audits) == 6, f"Expected 6 audit logs, got {len(audits)}"

        assert final_sim.current_day == 2, f"Expected current_day to be 2, but got {final_sim.current_day}"
