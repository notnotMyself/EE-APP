"""
Briefings API endpoints - 简报信息流接口

提供以下功能：
- 获取用户简报列表（信息流）
- 获取未读简报数量
- 标记简报为已读
- 从简报开始对话
- 忽略简报

注意：使用 Supabase Client 而不是 SQLAlchemy 直连，
因为 Supabase Pooler 连接存在认证问题。
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import get_current_active_user
# 使用 Supabase Client 版本的 CRUD（绕过 SQLAlchemy 直连问题）
from app.crud.crud_briefing_supabase import briefing_supabase as crud_briefing
from app.crud.crud_conversation_supabase import conversation_supabase as crud_conversation
from app.crud.crud_agent_supabase import agent_supabase as crud_agent
from app.schemas.briefing import (
    Briefing,
    BriefingWithAgent,
    BriefingListResponse,
    BriefingUnreadCount,
    BriefingStatus,
    StartConversationRequest,
    StartConversationResponse,
)
from app.schemas.conversation import ConversationCreate
from app.schemas.user import CurrentUser

router = APIRouter()


@router.get("/", response_model=BriefingListResponse)
async def list_my_briefings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[BriefingStatus] = Query(None, alias="status"),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    获取当前用户的简报列表（信息流）

    - **skip**: 跳过的条目数（分页）
    - **limit**: 返回的最大条目数
    - **status**: 筛选状态（new, read, actioned, dismissed）
    """
    status_value = status_filter.value if status_filter else None
    
    briefings = await crud_briefing.get_user_briefings(
        user_id=current_user.id,
        status=status_value,
        skip=skip,
        limit=limit
    )

    total = await crud_briefing.count_user_briefings(
        user_id=current_user.id,
        status=status_value
    )

    unread_info = await crud_briefing.get_unread_count(user_id=current_user.id)

    # 转换为响应模型
    items = [BriefingWithAgent(**b) for b in briefings]

    return BriefingListResponse(
        items=items,
        total=total,
        unread_count=unread_info["count"]
    )


@router.get("/unread-count", response_model=BriefingUnreadCount)
async def get_unread_count(
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    获取未读简报数量

    返回总数和按优先级分类的数量
    """
    unread_info = await crud_briefing.get_unread_count(user_id=current_user.id)

    return BriefingUnreadCount(
        count=unread_info["count"],
        by_priority=unread_info["by_priority"]
    )


@router.get("/{briefing_id}", response_model=BriefingWithAgent)
async def get_briefing(
    briefing_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    获取单个简报详情
    """
    briefing_data = await crud_briefing.get_with_agent(briefing_id=briefing_id)

    if not briefing_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not found"
        )

    # 检查权限
    if str(briefing_data.get('user_id')) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this briefing"
        )

    return BriefingWithAgent(**briefing_data)


@router.patch("/{briefing_id}/read", response_model=Briefing)
async def mark_as_read(
    briefing_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    标记简报为已读
    """
    # 先获取并验证权限
    briefing = await crud_briefing.get(briefing_id=briefing_id)

    if not briefing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not found"
        )

    if str(briefing.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this briefing"
        )

    updated = await crud_briefing.mark_as_read(briefing_id=briefing_id)
    return updated


@router.post("/{briefing_id}/start-conversation", response_model=StartConversationResponse)
async def start_conversation_from_briefing(
    briefing_id: UUID,
    request: StartConversationRequest = None,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    从简报开始对话

    创建一个新对话，并将简报的上下文传入对话
    """
    # 获取简报
    briefing = await crud_briefing.get(briefing_id=briefing_id)

    if not briefing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not found"
        )

    if str(briefing.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this briefing"
        )

    # 如果已有关联对话，直接返回
    if briefing.get("conversation_id"):
        return StartConversationResponse(
            conversation_id=UUID(briefing["conversation_id"]),
            briefing_id=briefing_id
        )

    agent_id = UUID(briefing["agent_id"])

    # 如果该用户 + 该 Agent 已存在 conversation（唯一约束），直接复用
    existing_conversation = await crud_conversation.get_by_user_agent(
        user_id=current_user.id,
        agent_id=agent_id,
    )
    if existing_conversation:
        await crud_briefing.mark_as_actioned(
            briefing_id=briefing_id,
            conversation_id=UUID(existing_conversation["id"]),
        )
        return StartConversationResponse(
            conversation_id=UUID(existing_conversation["id"]),
            briefing_id=briefing_id,
        )

    # 获取 Agent 信息
    agent = await crud_agent.get(agent_id=agent_id)
    if not agent or not agent.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # 构建对话上下文
    context = {
        "source": "briefing",
        "briefing_id": str(briefing_id),
        "briefing_title": briefing.get("title"),
        "briefing_summary": briefing.get("summary"),
        "briefing_context": briefing.get("context_data"),
        "initial_prompt": request.prompt if request else None
    }

    # 创建对话
    conversation_in = ConversationCreate(
        agent_id=agent_id,
        title=f"关于：{briefing.get('title')}",
        context=context
    )

    conversation = await crud_conversation.create(
        user_id=current_user.id,
        obj_in=conversation_in.model_dump()
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

    # 更新简报状态
    await crud_briefing.mark_as_actioned(
        briefing_id=briefing_id,
        conversation_id=UUID(conversation["id"])
    )

    return StartConversationResponse(
        conversation_id=UUID(conversation["id"]),
        briefing_id=briefing_id
    )


@router.delete("/{briefing_id}")
async def dismiss_briefing(
    briefing_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    忽略/删除简报
    """
    briefing = await crud_briefing.get(briefing_id=briefing_id)

    if not briefing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not found"
        )

    if str(briefing.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this briefing"
        )

    await crud_briefing.dismiss(briefing_id=briefing_id)

    return {"message": "Briefing dismissed"}
