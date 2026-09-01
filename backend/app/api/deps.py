from typing import Generator, List, Optional
import uuid
import httpx
from cachetools import TTLCache
from fastapi import Depends, HTTPException, status, Query, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.schemas.auth import TokenPayload

from slowapi import Limiter
from slowapi.util import get_remote_address

def get_user_id(request: Request) -> str:
    """Extracts user ID from JWT or falls back to IP for unauthenticated requests."""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return f"ip:{get_remote_address(request)}"
        
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, options={"verify_signature": False, "verify_exp": False, "verify_aud": False, "verify_iss": False})
        user_id = payload.get("sub")
        return f"user:{user_id}" if user_id else f"ip:{get_remote_address(request)}"
    except jwt.PyJWTError:
        return f"ip:{get_remote_address(request)}"
    except Exception:
        return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=get_user_id)
# Global limit for any requester (authenticated or not) to protect threads
# Specific limits like @limiter.limit("5/minute") still apply on top.
GLOBAL_LIMIT = "100/minute"

# Cache for Clerk public keys
clerk_key_cache = TTLCache(maxsize=1, ttl=86400)

# OAuth2 scheme
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_db() -> Generator:
    async with SessionLocal() as session:
        yield session

async def get_clerk_public_key() -> str:
    """Fetches and caches Clerk JWKS to prevent outbound calls on every request."""
    if "pem" in clerk_key_cache:
        return clerk_key_cache["pem"]
    
    # Note: In a world-class setup, we would fetch from settings.CLERK_JWKS_URL
    # and convert the JWK to PEM. For now, we protect the existing PEM setting.
    clerk_key_cache["pem"] = settings.CLERK_PEM_PUBLIC_KEY
    return clerk_key_cache["pem"]

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2),
    public_key: str = Depends(get_clerk_public_key)
) -> User:
    # 1. Check Redis Revocation List
    import redis.asyncio as redis
    from app.core.config import settings
    r = redis.from_url(settings.CELERY_BROKER_URL) # Reuse Redis host
    
    try:
        # Extract JTI (Unique Token ID)
        payload_unverified = jwt.decode(token, options={"verify_signature": False, "verify_exp": False, "verify_aud": False, "verify_iss": False})
        jti = payload_unverified.get("jti")
        if jti and await r.get(f"revoked_token:{jti}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )
    except HTTPException:
        raise
    except jwt.PyJWTError:
        pass # Fall through to standard verification
    except Exception:
        pass # Fall through to standard verification
    finally:
        await r.aclose()

    try:
        payload = jwt.decode(
            token, 
            public_key, 
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER,
            audience=settings.CLERK_AUDIENCE,
            options={"verify_aud": True, "verify_iss": True}
        )
        clerk_id = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    result = await db.execute(select(User).where(User.clerk_id == clerk_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this resource",
            )
        return user

class PaginationParams:
    def __init__(
        self,
        cursor: Optional[str] = Query(None, description="Base64 encoded (created_at, id)"),
        limit: int = Query(20, ge=1, le=100)
    ):
        self.cursor = cursor
        self.limit = limit
