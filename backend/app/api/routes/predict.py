from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.deps import get_db, get_current_user, limiter
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute") # Strict limit for compute-intensive SHAP inference
async def create_prediction(
    request: Request, # Required by slowapi
    prediction_req: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    On-demand epidemiological inference with SHAP attribution.
    Rate-limited to 5 requests per minute to prevent resource exhaustion.
    """
    service = PredictionService(db)
    try:
        result = await service.predict_single(
            district_id=prediction_req.district_id,
            disease=prediction_req.disease,
            as_of_date=prediction_req.prediction_date,
            overrides=prediction_req.overrides,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INSUFFICIENT_HISTORY", "message": "Insufficient history for prediction"},
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Inference engine failure: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Inference engine failure"
        )
