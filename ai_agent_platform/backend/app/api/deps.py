"""API Dependencies."""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db.supabase import get_supabase_client
from app.schemas.user import CurrentUser


# Security scheme
security = HTTPBearer()


async def get_db() -> Generator[AsyncSession, None, None]:
    """
    Get database session (SQLAlchemy).
    注意：大多数端点已迁移到 Supabase Client，此函数仅为兼容保留。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Get current user by verifying Supabase JWT with Supabase Auth."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        supabase = get_supabase_client()

        # supabase-py v2 API compatibility: get_user(token) vs get_user(jwt=token)
        try:
            user_response = supabase.auth.get_user(token)
        except TypeError:
            user_response = supabase.auth.get_user(jwt=token)

        sb_user = getattr(user_response, "user", None) or getattr(user_response, "data", None)
        if sb_user is None:
            # Some versions return dict-like
            try:
                sb_user = user_response.get("user")  # type: ignore[attr-defined]
            except Exception:
                sb_user = None

        if sb_user is None:
            raise credentials_exception

        user_id = getattr(sb_user, "id", None) or (sb_user.get("id") if isinstance(sb_user, dict) else None)
        email = getattr(sb_user, "email", None) or (sb_user.get("email") if isinstance(sb_user, dict) else None)
        if not user_id:
            raise credentials_exception

        return CurrentUser(id=str(user_id), email=email, is_active=True, is_superuser=False)

    except HTTPException:
        raise
    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
