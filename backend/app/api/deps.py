from typing import Generator, List, Optional
import uuid
import httpx
from cachetools import TTLCache
from fastapi import Depends, HTTPException, status, Query, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
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
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")

        if alg == "HS256":
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        elif alg == "RS256":
            # Read public key asynchronously in a synchronous context
            # In a real app we might fetch the key on startup or pass it from app state,
            # but using settings directly is fine here since get_clerk_public_key()
            # currently falls back to `settings.CLERK_PEM_PUBLIC_KEY` anyway.
            # To be absolutely safe against get_clerk_public_key() logic changes later,
            # we should use the setting.
            payload = jwt.decode(
                token,
                settings.CLERK_PEM_PUBLIC_KEY,
                algorithms=["RS256"],
                issuer=settings.CLERK_ISSUER,
                audience=settings.CLERK_AUDIENCE,
                options={"verify_aud": True, "verify_iss": True}
            )
        else:
            raise ValueError("Unsupported algorithm")

        user_id = payload.get("sub")
        return f"user:{user_id}" if user_id else f"ip:{get_remote_address(request)}"
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
    import redis.asyncio as redis
    from app.core.config import settings

    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")
        if alg == "HS256":
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        elif alg == "RS256":
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                issuer=settings.CLERK_ISSUER,
                audience=settings.CLERK_AUDIENCE,
                options={"verify_aud": True, "verify_iss": True}
            )
        else:
            raise ValueError("Unsupported algorithm")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # 1. Check Redis Revocation List
    r = redis.from_url(settings.CELERY_BROKER_URL) # Reuse Redis host
    
    try:
        jti = payload.get("jti")
        if jti and await r.get(f"revoked_token:{jti}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )
    except HTTPException:
        raise
    except Exception:
        pass
    finally:
        await r.aclose()

    sub = payload.get("sub")
    if alg == "HS256":
        try:
            import uuid
            user_uuid = uuid.UUID(str(sub))
            result = await db.execute(select(User).where(User.id == user_uuid))
        except ValueError:
            result = await db.execute(select(User).where(User.id == sub))
    else:
        result = await db.execute(select(User).where(User.clerk_id == sub))
    
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
