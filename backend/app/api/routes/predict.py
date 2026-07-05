from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.api import deps
from app.api.deps import get_db, get_current_user, limiter
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

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
        logger.exception("Inference error (ValueError)")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INSUFFICIENT_HISTORY", "message": "Insufficient data to perform inference."},
        )
    except Exception as e:
        logger.exception("Inference engine failure")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Inference engine encountered an internal failure."
        )
