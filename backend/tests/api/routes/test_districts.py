import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.district import District
from app.models.alert import Alert, AlertStatus
import uuid

# A basic test to verify that the get_district_stats endpoint returns correctly formatted stats
@pytest.mark.asyncio
async def test_get_district_stats(db_session: AsyncSession):
    # Setup some test data
    d1 = District(name="Test1", state="TS", state_code="TS", population=1000000, disease_burden_history={})
    d2 = District(name="Test2", state="TS", state_code="TS", population=2000000, disease_burden_history={})
    db_session.add(d1)
    db_session.add(d2)
    await db_session.commit()

    a1 = Alert(district_id=d1.id, disease="dengue", risk_score=50, status=AlertStatus.TRIGGERED)
    a2 = Alert(district_id=d2.id, disease="dengue", risk_score=60, status=AlertStatus.RESOLVED)
    db_session.add(a1)
    db_session.add(a2)
    await db_session.commit()

    # We will test the implementation of the endpoint function directly
    from app.api.routes.districts import get_district_stats

    res = await get_district_stats(db=db_session)
    assert res["total_districts"] == 2
    assert res["population_covered"] == "3.0M"
    assert res["active_alerts"] == 1
