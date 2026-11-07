from typing import List, Any, Dict, Optional
from uuid import UUID
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.api import deps
from app.models.district import District
from app.services.prediction_service import PredictionService

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def list_districts(
    disease: str = Query("dengue", description="Disease type to filter by"),
    state: Optional[str] = Query(None, description="State code to filter by (e.g., 'KA')"),
    time_window: int = Query(14, description="Days to look back/forward"),
    jurisdiction_only: bool = Query(False, description="Filter to only districts watched by the current user"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    List districts with their baseline risk scores for a specific disease.
    """
    service = PredictionService(db)
    try:
        query = select(District)
        if state:
            query = query.where(District.state_code == state)
            
        if jurisdiction_only:
            query = query.join(District.users).where(District.users.any(id=current_user.id))

        result = await db.execute(query)
        districts = result.scalars().all()
        
        # Determine watched districts for the user
        watched_query = select(District.id).where(District.users.any(id=current_user.id))
        watched_result = await db.execute(watched_query)
        watched_ids = set(watched_result.scalars().all())

        # Batch predict all districts concurrently for significant performance boost
        # Reduced from N sequential calls to concurrent execution with controlled semaphore
        district_ids = [d.id for d in districts]
        predictions = await service.predict_batch(district_ids, disease, date.today())

        # Map predictions by district_id for easy lookup
        pred_map = {p.district_id: p for p in predictions}

        output = []
        for d in districts:
            pred = pred_map.get(d.id)
            if pred:
                output.append({
                    "id": str(d.id),
                    "name": d.name,
                    "state": d.state,
                    "state_code": d.state_code,
                    "risk_score": pred.risk_score,
                    "risk_tier": pred.risk_tier,
                    "last_updated": pred.prediction_date.isoformat(),
                    "extrapolation_warning": pred.extrapolation_warning,
                    "is_watched": d.id in watched_ids
                })
            else:
                output.append({
                    "id": str(d.id),
                    "name": d.name,
                    "state": d.state,
                    "state_code": d.state_code,
                    "risk_score": 0,
                    "risk_tier": "unknown",
                    "last_updated": "No Data",
                    "extrapolation_warning": False,
                    "is_watched": d.id in watched_ids
                })
            
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jurisdiction matrix: {str(e)}")

@router.post("/{district_id}/watch")
async def watch_district(
    district_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """Add a district to the user's jurisdiction watchlist."""
    from sqlalchemy.orm import selectinload

    result = await db.execute(select(District).options(selectinload(District.users)).where(District.id == district_id))
    district = result.scalar_one_or_none()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")

    # Check if user is already watching by checking IDs
    is_watching = any(u.id == current_user.id for u in district.users)
    if not is_watching:
        district.users.append(current_user)
        await db.commit()

    return {"status": "success", "message": f"Added {district.name} to jurisdiction."}

@router.delete("/{district_id}/watch")
async def unwatch_district(
    district_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """Remove a district from the user's jurisdiction watchlist."""
    from sqlalchemy.orm import selectinload

    result = await db.execute(select(District).options(selectinload(District.users)).where(District.id == district_id))
    district = result.scalar_one_or_none()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")

    # Find user by ID in district.users list
    user_to_remove = next((u for u in district.users if u.id == current_user.id), None)
    if user_to_remove:
        district.users.remove(user_to_remove)
        await db.commit()

    return {"status": "success", "message": f"Removed {district.name} from jurisdiction."}

@router.get("/{district_id}", response_model=Dict[str, Any])
async def get_district_detail(
    district_id: UUID,
    disease: str = Query("dengue"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Fetch full detail for a single district including latest prediction.
    """
    result = await db.execute(select(District).where(District.id == district_id))
    district = result.scalar_one_or_none()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
        
    service = PredictionService(db)
    try:
        pred = await service.predict_single(district.id, disease, date.today())
        return {
            "id": str(district.id),
            "name": district.name,
            "state": district.state,
            "population": district.population,
            "risk_score": pred.risk_score,
            "risk_tier": pred.risk_tier,
            "shap_values": pred.shap_values,
            "feature_snapshot": pred.feature_snapshot
        }
    except Exception as e:
        return {
            "id": str(district.id),
            "name": district.name,
            "state": district.state,
            "risk_score": 0,
            "risk_tier": "unknown",
            "error": str(e)
        }

@router.get("/stats", response_model=Dict[str, Any])
async def get_district_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Get aggregated mission statistics for the dashboard.
    """
    from sqlalchemy import func
    from app.models.district import District
    from app.models.alert import Alert
    
    # Total Districts
    q_total = await db.execute(select(func.count(District.id)))
    total = q_total.scalar() or 0
    
    # Population
    q_pop = await db.execute(select(func.sum(District.population)))
    pop = q_pop.scalar() or 0
    
    # Active Alerts
    q_alerts = await db.execute(select(func.count(Alert.id)).where(Alert.is_resolved == False))
    alerts = q_alerts.scalar() or 0
    
    return {
        "total_districts": total,
        "population_covered": f"{pop/1000000:.1f}M",
        "active_alerts": alerts,
        "avg_risk": 42.8 # Baseline
    }
