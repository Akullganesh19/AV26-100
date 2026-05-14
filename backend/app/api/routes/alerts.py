from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.api import deps
from app.core.database import get_db
from app.models.alert import Alert, AlertStatus
from app.models.district import District
from app.services.alert_service import AlertService

router = APIRouter()

@router.get("/", response_model=List[Any])
async def get_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieve clinical and autonomous alerts with district metadata.
    """
    query = (
        select(Alert, District.name.label("district_name"))
        .join(District, Alert.district_id == District.id)
        .order_by(desc(Alert.triggered_at))
        .limit(50)
    )
    result = await db.execute(query)
    
    alerts_with_names = []
    for row in result.all():
        alert, district_name = row
        alert_dict = {
            "id": str(alert.id),
            "district_name": district_name,
            "disease": alert.disease,
            "risk_score": float(alert.risk_score),
            "status": alert.status.value,
            "alert_type": alert.alert_type.value,
            "triggered_at": alert.triggered_at.isoformat(),
            "metadata_json": alert.metadata_json
        }
        alerts_with_names.append(alert_dict)
        
    return alerts_with_names

@router.post("/{alert_id}/acknowledge")
async def acknowledge_mission_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Officer sign-off on a tactical threat.
    """
    alert = await AlertService.acknowledge_alert(db, alert_id, current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "alert_id": alert_id}
