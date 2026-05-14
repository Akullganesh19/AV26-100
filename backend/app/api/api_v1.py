from fastapi import APIRouter
from app.api.routes import auth, predict, districts, alerts, scenarios, reports, clinical

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(predict.router, prefix="/predict", tags=["prediction"])
api_router.include_router(districts.router, prefix="/districts", tags=["districts"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(clinical.router, prefix="/clinical", tags=["clinical"])
