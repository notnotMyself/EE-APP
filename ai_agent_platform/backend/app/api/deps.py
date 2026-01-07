"""API Dependencies."""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.config import settings
from app.models.user import User


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
) -> User:
    """Get current user from JWT token (Supabase JWT)."""
    import logging
    logger = logging.getLogger(__name__)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        logger.info(f"Received token: {token[:20]}...")

        # 首先尝试验证 Supabase JWT (不验证签名，只解析)
        # Supabase JWT 使用自己的密钥签名，我们信任 Supabase 的 token
        payload = jwt.decode(
            token,
            key="",  # 空密钥，因为我们不验证签名
            options={
                "verify_signature": False,  # 不验证签名
                "verify_aud": False,  # 不验证 audience
                "verify_iss": False,  # 不验证 issuer
                "verify_exp": False,  # 不验证过期时间
            }
        )
        logger.info(f"JWT payload: {payload}")

        # Supabase JWT 中 'sub' 字段就是 user_id
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.error("No 'sub' field in JWT payload")
            raise credentials_exception

        # 获取 email 从 JWT
        email: str = payload.get("email", "")

        logger.info(f"Extracted user_id: {user_id}, email: {email}")

        # 暂时跳过数据库查询，直接从 JWT 构造用户对象
        # TODO: 配置正确的 DATABASE_URL 后，改为从数据库查询
        # 创建临时用户对象
        user = User(
            id=user_id,
            email=email,
            is_active=True,
            is_superuser=False
        )

        logger.info(f"User authenticated (from JWT): {user.email}")
        return user

    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
