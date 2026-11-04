from typing import List, Dict, Any, Optional
import hashlib
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.services.clinical_service import ClinicalService
from app.schemas.clinical import HeartScreeningInput, DiabetesScreeningInput, ParkinsonsScreeningInput
from app.api.deps import limiter, get_db
from app.models.audit_log import PredictionAuditLog

router = APIRouter()
clinical_service = ClinicalService()

from fastapi import BackgroundTasks
from app.services.alert_service import AlertService

from sqlalchemy import select, desc
from app.models.alert import Alert, AlertStatus

@router.get("/oracle/next-focus", response_model=Dict[str, Any])
@limiter.limit("20/minute")
async def predict_next_focus(
    request: Request,
    district_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Oracle: Predict the user's next clinical focus.
    If a district has an active clinical cluster alert, default to that disease.
    Otherwise, default to 'heart'.
    """
    default_focus = "heart"
    if not district_id:
        return {"focus": default_focus}

    try:
        # Find the most recent active alert for this district
        query = select(Alert).where(
            (Alert.district_id == district_id) &
            (Alert.status == AlertStatus.TRIGGERED)
        ).order_by(desc(Alert.triggered_at)).limit(1)

        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if alert and alert.disease in ["heart", "diabetes", "parkinsons"]:
            return {"focus": alert.disease}

        return {"focus": default_focus}
    except Exception as e:
        # Graceful degradation
        return {"focus": default_focus}


async def log_prediction(
    db: AsyncSession, 
    user_id: Any, 
    endpoint: str, 
    input_data: Any, 
    result: Optional[Dict[str, Any]] = None,
    status: str = "SUCCESS",
    error: Optional[str] = None,
    district_id: Optional[str] = None
):
    input_str = json.dumps(input_data, sort_keys=True, default=str)
    input_hash = hashlib.sha256(input_str.encode()).hexdigest()
    
    audit = PredictionAuditLog(
        user_id=user_id,
        district_id=district_id, # Link individual screening to mission sector
        endpoint=endpoint,
        input_hash=input_hash,
        risk_score=result["risk_score"] if result else 0.0,
        model_version=result["model_version"] if result else "unknown",
        status=status,
        metadata_json=json.dumps({"error": error}) if error else None
    )
    db.add(audit)
    await db.commit()

@router.post("/heart", response_model=Dict[str, Any])
@limiter.limit("5/minute")
@limiter.limit("50/hour")
async def diagnose_heart(
    request: Request,
    data: HeartScreeningInput,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Tactical diagnosis for Heart Disease using clinical metrics.
    """
    try:
        features = [
            data.age, data.sex, data.cp, data.trestbps, data.chol,
            data.fbs, data.restecg, data.thalach, data.exang,
            data.oldpeak, data.slope, data.ca, data.thal
        ]
        result = clinical_service.predict_heart(features)
        await log_prediction(db, current_user.id, "clinical/heart", data.dict(), result, district_id=data.district_id)
        
        # Trigger cluster evaluation in background if high risk
        if result["risk_score"] > 0.7 and data.district_id:
            background_tasks.add_task(AlertService.evaluate_clinical_cluster, db, data.district_id, "heart")
            
        return result
    except Exception as e:
        await log_prediction(db, current_user.id, "clinical/heart", data.dict(), status="FAIL", error=str(e), district_id=data.district_id)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/diabetes", response_model=Dict[str, Any])
@limiter.limit("5/minute")
@limiter.limit("50/hour")
async def diagnose_diabetes(
    request: Request,
    data: DiabetesScreeningInput,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Tactical diagnosis for Diabetes.
    """
    try:
        features = [
            data.pregnancies, data.glucose, data.blood_pressure,
            data.skin_thickness, data.insulin, data.bmi, data.dpf, data.age
        ]
        result = clinical_service.predict_diabetes(features)
        await log_prediction(db, current_user.id, "clinical/diabetes", data.dict(), result, district_id=data.district_id)
        
        if result["risk_score"] > 0.7 and data.district_id:
            background_tasks.add_task(AlertService.evaluate_clinical_cluster, db, data.district_id, "diabetes")

        return result
    except Exception as e:
        await log_prediction(db, current_user.id, "clinical/diabetes", data.dict(), status="FAIL", error=str(e), district_id=data.district_id)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parkinsons", response_model=Dict[str, Any])
@limiter.limit("5/minute")
@limiter.limit("50/hour")
async def diagnose_parkinsons(
    request: Request,
    data: ParkinsonsScreeningInput,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Tactical diagnosis for Parkinson's Disease.
    """
    try:
        result = clinical_service.predict_parkinsons(data.vocal_metrics)
        await log_prediction(db, current_user.id, "clinical/parkinsons", data.dict(), result, district_id=data.district_id)
        
        if result["risk_score"] > 0.7 and data.district_id:
            background_tasks.add_task(AlertService.evaluate_clinical_cluster, db, data.district_id, "parkinsons")

        return result
    except Exception as e:
        await log_prediction(db, current_user.id, "clinical/parkinsons", data.dict(), status="FAIL", error=str(e), district_id=data.district_id)
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse
import io
from app.services.report_service import ReportService

@router.post("/report", response_class=StreamingResponse)
@limiter.limit("5/minute")
async def generate_screening_report(
    request: Request,
    results: List[Dict[str, Any]],
    district: str = "Central Command",
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Generate a professional tactical PDF report for a set of screening results.
    """
    try:
        pdf_bytes = ReportService.generate_clinical_report(results, district)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=EpiSense_Screening_{datetime.now():%Y%m%d}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
