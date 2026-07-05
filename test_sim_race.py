import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Setup mock models just for the test to bypass ORM errors from the full app loading
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, ForeignKey, JSON
import uuid

Base = declarative_base()

class Scenario(Base):
    __tablename__ = "scenarios"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    total_days: Mapped[int] = mapped_column(nullable=False, default=14)

class SimulationState(Base):
    __tablename__ = "simulation_states"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    current_day: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

class ScenarioEvent(Base):
    __tablename__ = "scenario_events"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    day_offset: Mapped[int] = mapped_column(nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    district_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    disease: Mapped[str] = mapped_column(String(64), nullable=False)
    data_json: Mapped[dict] = mapped_column(JSON, nullable=False)

# Monkeypatch the service to use our local models
from app.services.simulation_service import SimulationService
import app.services.simulation_service as sim_svc_mod
sim_svc_mod.SimulationState = SimulationState
sim_svc_mod.Scenario = Scenario
sim_svc_mod.ScenarioEvent = ScenarioEvent

# Also mock these so advance_day doesn't fail
class MockAlertService:
    @staticmethod
    async def evaluate_clinical_cluster(db, *args, **kwargs):
        pass
sim_svc_mod.AlertService = MockAlertService

DATABASE_URL = "postgresql+asyncpg://episense:episense@localhost:5432/episense_test"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def test_race():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        scenario = Scenario(id=uuid.uuid4(), name="Test", total_days=10)
        db.add(scenario)
        await db.commit()
        sim = SimulationState(id=uuid.uuid4(), scenario_id=scenario.id, user_id=uuid.uuid4(), current_day=0, is_active=True)
        db.add(sim)
        await db.commit()
        sim_id = sim.id

    async def advance_task():
        async with async_session() as db:
            await SimulationService.advance_day(db, str(sim_id))

    tasks = [advance_task() for _ in range(5)]
    await asyncio.gather(*tasks)

    async with async_session() as db:
        result = await db.execute(text(f"SELECT current_day FROM simulation_states WHERE id = '{sim_id}'"))
        final_day = result.scalar()
        print(f"Final day after 5 concurrent advance_day calls: {final_day} (Expected: 5 if no race, or < 5 if race)")

if __name__ == "__main__":
    asyncio.run(test_race())
