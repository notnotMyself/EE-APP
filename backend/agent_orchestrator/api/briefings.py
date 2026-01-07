"""
简报API - GET/PATCH/DELETE /briefings
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

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
    briefings: List[dict]
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
    user_id: str = Query(..., description="用户ID"),
    status: Optional[str] = Query(None, description="过滤状态: new, read, actioned, dismissed"),
    agent_id: Optional[str] = Query(None, description="过滤Agent ID"),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
):
    """
    获取用户的简报列表

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

    return BriefingListResponse(**result)


@router.get("/{briefing_id}")
async def get_briefing(briefing_id: str):
    """获取简报详情"""
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    briefing = await briefing_service.get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")

    return briefing


@router.get("/{briefing_id}/report")
async def get_briefing_report(briefing_id: str):
    """
    获取简报关联的完整报告

    返回格式：
    - content: 完整的Markdown报告内容
    - format: 内容格式（默认markdown）
    - title: 报告标题
    - created_at: 创建时间（如果从artifact获取）
    """
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    report = await briefing_service.get_briefing_report(briefing_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this briefing")

    return report


@router.patch("/{briefing_id}/read")
async def mark_as_read(briefing_id: str):
    """标记简报为已读"""
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    success = await briefing_service.mark_as_read(briefing_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to mark briefing as read")

    return {"status": "success", "briefing_id": briefing_id}


@router.post("/{briefing_id}/action")
async def execute_action(briefing_id: str, request: BriefingActionRequest):
    """
    执行简报操作

    - view_report: 返回完整报告内容
    - start_conversation: 创建对话并返回对话ID
    - dismiss: 标记为已忽略
    """
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

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
async def delete_briefing(briefing_id: str):
    """删除简报"""
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    success = await briefing_service.delete_briefing(briefing_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete briefing")

    return {"status": "success", "briefing_id": briefing_id}


@router.get("/unread-count")
async def get_unread_count(user_id: str = Query(..., description="用户ID")):
    """获取未读简报数量"""
    if not briefing_service:
        raise HTTPException(status_code=500, detail="Briefing service not initialized")

    result = await briefing_service.list_briefings(user_id=user_id, limit=0)
    return {"unread_count": result["unread_count"]}
