from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core.database import get_db
from app.models.scenario import Scenario, SimulationState
from app.services.simulation_service import SimulationService

router = APIRouter()

@router.get("/", response_model=List[Any])
async def list_scenarios(
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """List all mission templates available in the Scenario Lab."""
    query = select(Scenario).where(Scenario.is_template == True)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{scenario_id}/start")
async def start_mission_simulation(
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """Initialize a specific playback session for the current officer."""
    sim = await SimulationService.create_simulation(db, scenario_id, current_user.id)
    return sim

@router.get("/active", response_model=Optional[Any])
async def get_active_simulation(
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """Retrieve the officer's current running mission state."""
    query = select(SimulationState).where(
        and_(
            SimulationState.user_id == current_user.id,
            SimulationState.is_active == True
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

@router.post("/active/advance")
async def advance_mission_clock(
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """Advance the mission clock by one day (Snapshot Playback)."""
    # Find active sim
    active_query = select(SimulationState).where(
        and_(
            SimulationState.user_id == current_user.id,
            SimulationState.is_active == True
        )
    )
    res = await db.execute(active_query)
    sim = res.scalar_one_or_none()
    
    if not sim:
        raise HTTPException(status_code=400, detail="No active simulation found")
        
    updated = await SimulationService.advance_day(db, str(sim.id))
    return updated

from typing import Optional
from sqlalchemy import and_
