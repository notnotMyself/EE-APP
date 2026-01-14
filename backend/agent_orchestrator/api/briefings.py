"""
简报API - GET/PATCH/DELETE /briefings
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from .deps import get_current_user_id

router = APIRouter(prefix="/api/v1/briefings", tags=["briefings"])

# 全局briefing_service引用，由main.py注入
briefing_service = None


def set_briefing_service(service):
    """设置briefing服务实例"""
    global briefing_service
    briefing_service = service


# ============================================
# 数据模型
# ============================================


class BriefingResponse(BaseModel):
    id: str
    agent_id: str
    briefing_type: str
    priority: str
    title: str
    summary: str
    impact: Optional[str]
    actions: List[dict]
    status: str
    importance_score: float
    created_at: str
    read_at: Optional[str]

    class Config:
        from_attributes = True


class BriefingListResponse(BaseModel):
    items: List[dict]  # Changed from 'briefings' to match frontend
    total: int
    unread_count: int


class BriefingActionRequest(BaseModel):
    action: str  # view_report, start_conversation, dismiss
    data: Optional[dict] = {}


# ============================================
# API端点
# ============================================


@router.get("", response_model=BriefingListResponse)
async def list_briefings(
    user_id: str = Depends(get_current_user_id),
    status: Optional[str] = Query(None, description="过滤状态: new, read, actioned, dismissed"),
    agent_id: Optional[str] = Query(None, description="过滤Agent ID"),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
):
    """
    获取用户的简报列表

    需要认证：需要在Header中提供有效的Bearer Token
    user_id将从JWT token中自动提取

    - 按创建时间倒序排列
    - 支持按状态和Agent过滤
    - 返回未读数量
    """
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    result = await briefing_service.list_briefings(
        user_id=user_id,
        status=status,
        agent_id=agent_id,
        limit=limit,
        offset=offset,
    )

    # Map 'briefings' to 'items' for frontend compatibility
    return BriefingListResponse(
        items=result.get("briefings", []),
        total=result.get("total", 0),
        unread_count=result.get("unread_count", 0),
    )


@router.get("/{briefing_id}")
async def get_briefing(
    briefing_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    获取简报详情

    需要认证：需要在Header中提供有效的Bearer Token
    会验证该简报是否属于当前用户
    """
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    briefing = await briefing_service.get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")

    # 验证权限：确保该简报属于当前用户
    if briefing.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return briefing


@router.get("/{briefing_id}/report")
async def get_briefing_report(
    briefing_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    获取简报关联的完整报告

    需要认证：需要在Header中提供有效的Bearer Token
    会验证该简报是否属于当前用户

    返回格式：
    - content: 完整的Markdown报告内容
    - format: 内容格式（默认markdown）
    - title: 报告标题
    - created_at: 创建时间（如果从artifact获取）
    """
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    # 先验证权限
    briefing = await briefing_service.get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
    if briefing.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    report = await briefing_service.get_briefing_report(briefing_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this briefing")

    return report


@router.patch("/{briefing_id}/read")
async def mark_as_read(
    briefing_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    标记简报为已读

    需要认证：需要在Header中提供有效的Bearer Token
    会验证该简报是否属于当前用户
    """
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    # 先验证权限
    briefing = await briefing_service.get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
    if briefing.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = await briefing_service.mark_as_read(briefing_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to mark briefing as read")

    return {"status": "success", "briefing_id": briefing_id}


@router.post("/{briefing_id}/action")
async def execute_action(
    briefing_id: str,
    request: BriefingActionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    执行简报操作

    需要认证：需要在Header中提供有效的Bearer Token
    会验证该简报是否属于当前用户

    - view_report: 返回完整报告内容
    - start_conversation: 创建对话并返回对话ID
    - dismiss: 标记为已忽略
    """
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    # 先验证权限
    briefing = await briefing_service.get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
    if briefing.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        result = await briefing_service.execute_action(
            briefing_id=briefing_id,
            action=request.action,
            data=request.data,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{briefing_id}")
async def delete_briefing(
    briefing_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    删除简报

    需要认证：需要在Header中提供有效的Bearer Token
    会验证该简报是否属于当前用户
    """
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    # 先验证权限
    briefing = await briefing_service.get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
    if briefing.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = await briefing_service.delete_briefing(briefing_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete briefing")

    return {"status": "success", "briefing_id": briefing_id}


@router.get("/unread-count")
async def get_unread_count(user_id: str = Depends(get_current_user_id)):
    """
    获取未读简报数量

    需要认证：需要在Header中提供有效的Bearer Token
    user_id将从JWT token中自动提取
    """
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    result = await briefing_service.list_briefings(user_id=user_id, limit=0)
    # Return 'count' instead of 'unread_count' for frontend compatibility
    return {"count": result["unread_count"], "by_priority": {}}
