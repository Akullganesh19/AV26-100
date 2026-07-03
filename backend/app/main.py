import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.api_v1 import api_router
from app.core.config import settings
from app.api.deps import get_db, limiter
from app.services.prediction_service import load_artifacts, ml_state
from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.logging import setup_logging

# Initialize Structured Logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Load all ML artifacts (Atomic — fails if any are missing/corrupt)
    logger.info("Initializing ML artifacts...")
    try:
        artifacts = load_artifacts()
        ml_state.update(artifacts)
        logger.info("ML context initialized", extra={"version": ml_state["manifest"]["version"]})
    except Exception as e:
        logger.critical("Failed to load ML artifacts", exc_info=True)
        raise RuntimeError(f"System cannot start without ML models: {e}")

    # 2. Start Background Scheduler
    start_scheduler()
    logger.info("Background scheduler started")
    
    yield
    
    # 3. Shutdown: Clean up state and scheduler
    stop_scheduler()
    ml_state.clear()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="EpiSense Intelligence Platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Rate Limiting & Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS Configuration
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://*.clerk.accounts.dev; " # Authorized Clerk Scripts
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: blob: https://img.clerk.com; " # Allow Clerk User Images
        "connect-src 'self' https://*.clerk.accounts.dev; "
        "frame-src https://*.clerk.accounts.dev; " # Allow Clerk Auth IFrames
        "frame-ancestors 'none';"
    )
    return response

# Routing
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Service health probe with DB connectivity check.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "service": "episense-core",
            "database": "connected",
            "model_version": ml_state.get("manifest", {}).get("version", "unknown")
        }
    except Exception as e:
        logger.error("Health check failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service infrastructure unavailable",
        )

@app.get("/api/ready")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """
    Standard readiness probe checking DB + Redis + ML state.
    """
    checks = {"database": False, "redis": False, "ml_artifacts": len(ml_state) > 0}
    try:
        # DB Check
        await db.execute(text("SELECT 1"))
        checks["database"] = True
        
        # Redis Check (using asyncio client)
        import redis.asyncio as redis
        r = redis.from_url(settings.CELERY_BROKER_URL)
        await r.ping()
        await r.aclose()
        checks["redis"] = True
        
        if all(checks.values()):
            return {"status": "ready", "dependencies": checks}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service partially available: {checks}",
            )
    except Exception as e:
        # Sentinel: Avoid leaking system internals in error messages
        logger.error("Readiness check failed", extra={"checks": checks, "error_type": type(e).__name__}, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready",
        )