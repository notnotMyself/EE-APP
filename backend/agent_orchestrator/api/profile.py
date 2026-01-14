"""
个人中心API - Profile endpoints

提供用户信息和使用统计的REST API：
- GET /profile/usage-stats - 获取用户使用统计
- GET /profile/subscribed-agents - 获取订阅的AI员工列表
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .deps import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])

# 全局服务引用，由main.py注入
conversation_service = None
briefing_service = None


def set_services(conv_service, brief_service):
    """设置服务实例"""
    global conversation_service, briefing_service
    conversation_service = conv_service
    briefing_service = brief_service


# ============================================
# 数据模型 (Pydantic Schemas)
# ============================================


class UsageStats(BaseModel):
    """使用统计模型"""

    total_briefings: int  # 收到简报总数
    weekly_briefings: int  # 本周新增简报
    active_conversations: int  # 进行中的对话
    total_messages: int  # 累计对话轮次

    class Config:
        from_attributes = True


class SubscribedAgent(BaseModel):
    """订阅的AI员工模型"""

    id: str
    name: str
    role: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    subscribed_at: str

    class Config:
        from_attributes = True


# ============================================
# API端点
# ============================================


@router.get("/usage-stats", response_model=UsageStats)
async def get_usage_stats(
    user_id: str = Depends(get_current_user_id),
):
    """
    获取用户使用统计

    需要认证：需要在Header中提供有效的Bearer Token
    user_id将从JWT token中自动提取

    Returns:
        使用统计数据
    """
    if not conversation_service or not briefing_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    try:
        # 获取简报统计
        total_briefings = await _count_total_briefings(user_id)
        weekly_briefings = await _count_weekly_briefings(user_id)

        # 获取对话统计
        active_conversations = await _count_active_conversations(user_id)
        total_messages = await _count_total_messages(user_id)

        return UsageStats(
            total_briefings=total_briefings,
            weekly_briefings=weekly_briefings,
            active_conversations=active_conversations,
            total_messages=total_messages,
        )

    except Exception as e:
        logger.error(f"Error getting usage stats for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscribed-agents", response_model=List[SubscribedAgent])
async def get_subscribed_agents(
    user_id: str = Depends(get_current_user_id),
):
    """
    获取用户订阅的AI员工列表

    需要认证：需要在Header中提供有效的Bearer Token
    user_id将从JWT token中自动提取

    Returns:
        订阅的AI员工列表
    """
    if not conversation_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    try:
        # 通过对话记录推断订阅的AI员工
        # TODO: 未来可能需要单独的订阅表
        conversations = await conversation_service.list_user_conversations(
            user_id=user_id, limit=100
        )

        # 去重并获取唯一的agent_id列表
        agent_ids = list({conv["agent_id"] for conv in conversations})

        # 获取agent信息
        agents = []
        for agent_id in agent_ids:
            agent_info = await _get_agent_info(agent_id)
            if agent_info:
                agents.append(agent_info)

        return agents

    except Exception as e:
        logger.error(f"Error getting subscribed agents for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 辅助函数
# ============================================


async def _count_total_briefings(user_id: str) -> int:
    """统计用户收到的简报总数"""
    try:
        from models import supabase_client

        response = (
            supabase_client.table("briefings")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        return response.count or 0
    except Exception as e:
        logger.error(f"Error counting total briefings: {e}")
        return 0


async def _count_weekly_briefings(user_id: str) -> int:
    """统计用户本周收到的简报数"""
    try:
        from models import supabase_client
        from datetime import datetime, timedelta

        # 获取本周一的日期
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start_str = week_start.strftime("%Y-%m-%d 00:00:00")

        response = (
            supabase_client.table("briefings")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .gte("created_at", week_start_str)
            .execute()
        )
        return response.count or 0
    except Exception as e:
        logger.error(f"Error counting weekly briefings: {e}")
        return 0


async def _count_active_conversations(user_id: str) -> int:
    """统计用户进行中的对话数"""
    try:
        from models import supabase_client

        response = (
            supabase_client.table("conversations")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("status", "active")
            .execute()
        )
        return response.count or 0
    except Exception as e:
        logger.error(f"Error counting active conversations: {e}")
        return 0


async def _count_total_messages(user_id: str) -> int:
    """统计用户累计对话轮次"""
    try:
        from models import supabase_client

        # 首先获取用户的所有对话ID
        conversations_response = (
            supabase_client.table("conversations")
            .select("id")
            .eq("user_id", user_id)
            .execute()
        )

        if not conversations_response.data:
            return 0

        conversation_ids = [conv["id"] for conv in conversations_response.data]

        # 统计这些对话的消息总数
        response = (
            supabase_client.table("conversation_messages")
            .select("id", count="exact")
            .in_("conversation_id", conversation_ids)
            .execute()
        )
        return response.count or 0
    except Exception as e:
        logger.error(f"Error counting total messages: {e}")
        return 0


async def _get_agent_info(agent_id: str) -> Optional[SubscribedAgent]:
    """获取AI员工信息"""
    try:
        from models import supabase_client

        response = (
            supabase_client.table("agents").select("*").eq("id", agent_id).execute()
        )

        if not response.data:
            return None

        agent = response.data[0]

        # 获取用户首次与该agent对话的时间作为订阅时间
        conversations_response = (
            supabase_client.table("conversations")
            .select("created_at")
            .eq("agent_id", agent_id)
            .order("created_at", desc=False)
            .limit(1)
            .execute()
        )

        subscribed_at = (
            conversations_response.data[0]["created_at"]
            if conversations_response.data
            else agent.get("created_at", "")
        )

        return SubscribedAgent(
            id=agent["id"],
            name=agent["name"],
            role=agent["role"],
            description=agent.get("description"),
            avatar_url=agent.get("avatar_url"),
            subscribed_at=subscribed_at,
        )
    except Exception as e:
        logger.error(f"Error getting agent info for {agent_id}: {e}")
        return None
