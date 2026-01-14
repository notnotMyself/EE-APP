"""
认证依赖
为agent_orchestrator后端API提供认证保护
"""

import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

# 安全方案：使用Bearer Token
security = HTTPBearer()

# Supabase配置（从环境变量读取）
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')


def get_supabase_admin() -> Client:
    """
    获取Supabase Admin Client
    使用Service Role Key，拥有完全权限
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "Supabase配置未设置。请确保环境变量 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 已配置"
        )

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    验证Supabase JWT Token并返回当前用户ID

    使用方法：
    ```python
    @router.get("/some-endpoint")
    async def some_endpoint(user_id: str = Depends(get_current_user_id)):
        # user_id 是经过验证的当前用户ID
        ...
    ```

    Args:
        credentials: HTTP Bearer Token

    Returns:
        str: 用户ID (UUID格式)

    Raises:
        HTTPException: 401 - Token无效或已过期
    """
    token = credentials.credentials
    supabase = get_supabase_admin()

    try:
        # 使用Supabase验证Token
        user_response = supabase.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return str(user_response.user.id)

    except Exception as e:
        # 记录错误（生产环境应使用日志系统）
        print(f"认证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证或Token已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[str]:
    """
    可选的用户认证
    如果提供Token则验证，否则返回None

    用于某些可以匿名访问但有Token时提供增强功能的端点

    Args:
        credentials: 可选的HTTP Bearer Token

    Returns:
        Optional[str]: 用户ID或None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        supabase = get_supabase_admin()
        user_response = supabase.auth.get_user(token)

        if user_response.user:
            return str(user_response.user.id)

    except Exception:
        pass

    return None
