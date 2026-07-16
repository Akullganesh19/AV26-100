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
            
        result = await db.execute(query)
        districts = result.scalars().all()
        
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
                    "extrapolation_warning": pred.extrapolation_warning
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
                    "extrapolation_warning": False
                })
            
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jurisdiction matrix: {str(e)}")

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
    
    # Optimised by Bolt: Combine multiple queries into a single call using scalar subqueries.
    # AsyncSession is not thread-safe, so asyncio.gather() cannot be used here.
    query = select(
        select(func.count(District.id)).scalar_subquery().label("total_districts"),
        select(func.sum(District.population)).scalar_subquery().label("population"),
        select(func.count(Alert.id)).where(Alert.is_resolved == False).scalar_subquery().label("active_alerts")
    )
    result = await db.execute(query)
    row = result.fetchone()
    
    total = row.total_districts if row and row.total_districts else 0
    pop = row.population if row and row.population else 0
    alerts = row.active_alerts if row and row.active_alerts else 0
    
    return {
        "total_districts": total,
        "population_covered": f"{pop/1000000:.1f}M",
        "active_alerts": alerts,
        "avg_risk": 42.8 # Baseline
    }
